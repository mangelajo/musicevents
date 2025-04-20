import requests
import logging
from django.conf import settings
from events.models import Artist, Venue, Event
from django.utils import timezone
from datetime import datetime
from .image_utils import download_and_save_image  # Import the function

logger = logging.getLogger(__name__)

# Ticketmaster API base URL

TICKETMASTER_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

def fetch_events_for_city(city, state=None, api_key=None, size=20):
    """
    Fetch events from Ticketmaster API for a specific city
    
    Args:
        city (str): City name
        state (str, optional): State code (e.g., 'CA', 'NY')
        api_key (str, optional): Ticketmaster API key, defaults to settings.TICKETMASTER_API_KEY
        size (int, optional): Number of events to fetch, defaults to 20
        
    Returns:
        dict: API response data
    """
    if not api_key:
        api_key = getattr(settings, 'TICKETMASTER_API_KEY', None)
        
    if not api_key:
        logger.error("Ticketmaster API key not provided")
        return {"error": "API key not provided"}
    
    params = {
        "apikey": api_key,
        "city": city,
        "size": size,
        "classificationName": "music",
        "sort": "date,asc"
    }
    
    if state:
        params["stateCode"] = state
    
    try:
        response = requests.get(TICKETMASTER_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching events from Ticketmaster: {e}")
        return {"error": str(e)}

def sync_events_for_city(city, state=None, api_key=None):
    """
    Sync events from Ticketmaster API to the database
    
    Args:
        city (str): City name
        state (str, optional): State code (e.g., 'CA', 'NY')
        api_key (str, optional): Ticketmaster API key
        
    Returns:
        tuple: (created_count, updated_count, error_message)
    """
    data = fetch_events_for_city(city, state, api_key)
    
    if "error" in data:
        return 0, 0, data["error"]
    
    if "_embedded" not in data or "events" not in data["_embedded"]:
        return 0, 0, "No events found"
    
    events = data["_embedded"]["events"]
    created_count = 0
    updated_count = 0
    
    for event_data in events:
        try:
            # Extract event details
            event_id = event_data["id"]
            event_name = event_data["name"]
            
            # Get date and time
            if "dates" in event_data and "start" in event_data["dates"]:
                start_date = event_data["dates"]["start"].get("dateTime")
                if not start_date:
                    # If no datetime, try to use local date with a default time
                    local_date = event_data["dates"]["start"].get("localDate")
                    if local_date:
                        start_date = f"{local_date}T19:00:00Z"  # Default to 7 PM
                    else:
                        continue  # Skip if no date available
            else:
                continue  # Skip if no date information
            
            # Convert to datetime object
            event_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            event_date = timezone.make_aware(event_date) if timezone.is_naive(event_date) else event_date
            
            # Get venue information
            venue_name = "Unknown Venue"
            venue_address = ""
            venue_city = city
            venue_state = state or ""
            venue_zip = ""
            venue_url = ""
            
            if "_embedded" in event_data and "venues" in event_data["_embedded"] and event_data["_embedded"]["venues"]:
                venue_data = event_data["_embedded"]["venues"][0]
                venue_name = venue_data.get("name", venue_name)
                
                if "address" in venue_data:
                    venue_address = venue_data["address"].get("line1", "")
                
                if "city" in venue_data:
                    venue_city = venue_data["city"].get("name", city)
                
                if "state" in venue_data:
                    venue_state = venue_data["state"].get("stateCode", state or "")
                
                if "postalCode" in venue_data:
                    venue_zip = venue_data.get("postalCode", "")
                
                if "url" in venue_data:
                    venue_url = venue_data.get("url", "")
            
            # Get ticket information
            ticket_url = event_data.get("url", "")
            ticket_price = None
            if "priceRanges" in event_data and event_data["priceRanges"]:
                price_range = event_data["priceRanges"][0]
                ticket_price = price_range.get("min", None)
            
            # Get image URL
            image_url = ""
            if "images" in event_data and event_data["images"]:
                # Find the best image (prefer 16:9 ratio with highest resolution)
                best_image = None
                best_width = 0
                
                for img in event_data["images"]:
                    # Check if it's a 16:9 ratio image
                    if img.get("ratio") == "16_9" and img.get("width", 0) > best_width:
                        best_image = img
                        best_width = img.get("width", 0)
                
                # If no 16:9 image found, use the first one
                if not best_image and event_data["images"]:
                    best_image = event_data["images"][0]
                
                if best_image:
                    image_url = best_image.get("url", "")
            
            # Get description
            description = ""
            if "info" in event_data:
                description = event_data.get("info", "")
            elif "description" in event_data:
                description = event_data.get("description", "")
            
            # Get artists/attractions
            artist_names = []
            if "_embedded" in event_data and "attractions" in event_data["_embedded"] and event_data["_embedded"]["attractions"]:
                for attraction in event_data["_embedded"]["attractions"]:
                    artist_names.append(attraction.get("name", ""))
            
            # Create or update venue
            venue, venue_created = Venue.objects.get_or_create(
                name=venue_name,
                city=venue_city,
                defaults={
                    "address": venue_address,
                    "state": venue_state,
                    "zip_code": venue_zip,
                    "website": venue_url,
                }
            )
            
            # Create or update event
            event, event_created = Event.objects.get_or_create(
                title=event_name,
                date=event_date,
                venue=venue,
                defaults={
                    "description": description,
                    "ticket_url": ticket_url,
                    "ticket_price": ticket_price,
                    "external_id": event_id,
                    "image_url": image_url,
                }
            )
            
            if event_created:
                created_count += 1
                # Download and save the image for new events
                if image_url:
                    download_and_save_image(image_url, event)
                    # Generate thumbnail
                    if event.image:
                        event.generate_thumbnail()
            else:
                # Update existing event
                event.description = description
                event.ticket_url = ticket_url
                if ticket_price:
                    event.ticket_price = ticket_price
                event.external_id = event_id
                
                # Update image if URL has changed
                if image_url and event.image_url != image_url:
                    event.image_url = image_url
                    download_and_save_image(image_url, event)
                    # Generate thumbnail
                    if event.image:
                        event.generate_thumbnail()
                elif not event.image and event.image_url:
                    # Try to download image again if we have a URL but no image
                    download_and_save_image(event.image_url, event)
                    # Generate thumbnail
                    if event.image:
                        event.generate_thumbnail()
                
                event.save()
                updated_count += 1
            
            # Create artists and associate with event
            for artist_name in artist_names:
                artist, _ = Artist.objects.get_or_create(
                    name=artist_name,
                    defaults={
                        "bio": f"Artist/performer appearing at {event_name}",
                    }
                )
                event.artists.add(artist)
                
        except Exception as e:
            logger.error(f"Error processing event {event_data.get('name', 'Unknown')}: {e}")
    
    return created_count, updated_count, None