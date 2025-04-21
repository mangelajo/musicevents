import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from .sync_base import EventSyncBase

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

class TicketmasterEventSync(EventSyncBase):
    """Ticketmaster event synchronization implementation."""

    def __init__(self, city, state=None, api_key=None):
        super().__init__('ticketmaster')
        self.city = city
        self.state = state
        self.api_key = api_key or getattr(settings, 'TICKETMASTER_API_KEY', None)

    def sync_events(self):
        """
        Sync events from Ticketmaster API to the database.
        
        Returns:
            tuple: (created_count, updated_count, error_message)
        """
        data = fetch_events_for_city(self.city, self.state, self.api_key)
        
        if "error" in data:
            return 0, 0, data["error"]
        
        if "_embedded" not in data or "events" not in data["_embedded"]:
            return 0, 0, "No events found"
        
        events = data["_embedded"]["events"]
        
        for event_data in events:
            try:
                # Process venue
                venue_data = self._extract_venue_data(event_data)
                venue, _ = self.create_or_update_venue(venue_data)
                if not venue:
                    continue

                # Process event
                processed_event_data = self._extract_event_data(event_data, venue)
                event, created = self.create_or_update_event(processed_event_data, venue)
                if not event:
                    continue

                # Process artists
                artist_names = self._extract_artist_names(event_data)
                for artist_name in artist_names:
                    artist_data = {
                        'name': artist_name,
                        'bio': f"Artist/performer appearing at {processed_event_data['title']}"
                    }
                    artist, _ = self.create_or_update_artist(artist_data)
                    if artist:
                        event.artists.add(artist)
                
            except Exception as e:
                logger.error(f"Error processing event {event_data.get('name', 'Unknown')}: {e}")
                self.error_count += 1
        
        return self.created_count, self.updated_count, None

    def _extract_venue_data(self, event_data):
        """Extract venue data from Ticketmaster event data."""
        venue_data = {
            'name': "Unknown Venue",
            'address': "",
            'city': self.city,
            'state': self.state or "",
            'zip_code': "",
            'website': ""
        }
        
        if "_embedded" in event_data and "venues" in event_data["_embedded"] and event_data["_embedded"]["venues"]:
            venue = event_data["_embedded"]["venues"][0]
            venue_data.update({
                'name': venue.get("name", venue_data['name']),
                'address': venue.get("address", {}).get("line1", ""),
                'city': venue.get("city", {}).get("name", self.city),
                'state': venue.get("state", {}).get("stateCode", self.state or ""),
                'zip_code': venue.get("postalCode", ""),
                'website': venue.get("url", "")
            })
        
        return venue_data

    def _extract_event_data(self, event_data, venue):
        """Extract event data from Ticketmaster event data."""
        # Get date and time
        event_date = self._parse_event_date(event_data)
        if not event_date:
            return None

        # Get image URL
        image_url = self._get_best_image_url(event_data)
        
        # Get ticket information
        ticket_url = event_data.get("url", "")
        ticket_price = None
        if "priceRanges" in event_data and event_data["priceRanges"]:
            price_range = event_data["priceRanges"][0]
            ticket_price = price_range.get("min", None)

        # Get description
        description = event_data.get("info", "") or event_data.get("description", "")

        return {
            'title': event_data["name"],
            'date': event_date,
            'description': description,
            'ticket_url': ticket_url,
            'ticket_price': ticket_price,
            'external_id': event_data["id"],
            'image_url': image_url
        }

    def _parse_event_date(self, event_data):
        """Parse event date from Ticketmaster data."""
        if "dates" not in event_data or "start" not in event_data["dates"]:
            return None

        start_date = event_data["dates"]["start"].get("dateTime")
        if not start_date:
            # If no datetime, try to use local date with a default time
            local_date = event_data["dates"]["start"].get("localDate")
            if local_date:
                start_date = f"{local_date}T19:00:00Z"  # Default to 7 PM
            else:
                return None

        # Convert to datetime object
        event_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        return timezone.make_aware(event_date) if timezone.is_naive(event_date) else event_date

    def _get_best_image_url(self, event_data):
        """Get the best available image URL from event data."""
        if not event_data.get("images"):
            return ""

        # Find the best image (prefer 16:9 ratio with highest resolution)
        best_image = None
        best_width = 0
        
        for img in event_data["images"]:
            if img.get("ratio") == "16_9" and img.get("width", 0) > best_width:
                best_image = img
                best_width = img.get("width", 0)
        
        # If no 16:9 image found, use the first one
        if not best_image and event_data["images"]:
            best_image = event_data["images"][0]
        
        return best_image.get("url", "") if best_image else ""

    def _extract_artist_names(self, event_data):
        """Extract artist names from event data."""
        artist_names = []
        if "_embedded" in event_data and "attractions" in event_data["_embedded"]:
            for attraction in event_data["_embedded"]["attractions"]:
                artist_names.append(attraction.get("name", ""))
        return artist_names


def sync_events_for_city(city, state=None, api_key=None):
    """
    Sync events from Ticketmaster API to the database.
    Wrapper function for backward compatibility.
    
    Args:
        city (str): City name
        state (str, optional): State code (e.g., 'CA', 'NY')
        api_key (str, optional): Ticketmaster API key
        
    Returns:
        tuple: (created_count, updated_count, error_message)
    """
    syncer = TicketmasterEventSync(city, state, api_key)
    return syncer.sync_events()