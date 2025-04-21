"""
Utility for synchronizing events from Sala Riviera website.
"""
import logging
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from django.utils import timezone
from django.utils.text import slugify
from .sync_base import EventSyncBase

logger = logging.getLogger(__name__)

# URL for Sala Riviera events
RIVIERA_URL = "https://salariviera.com/conciertossalariviera/"

# Venue information for Sala Riviera
VENUE_INFO = {
    "name": "La Riviera",
    "address": "Paseo Bajo de la Virgen del Puerto, s/n",
    "city": "Madrid",
    "state": "Madrid",
    "zip_code": "28005",
    "website": "https://salariviera.com/",
    "capacity": 2500
}

def fetch_riviera_events():
    """
    Fetch events from Sala Riviera website.
    
    Returns:
        list: List of event dictionaries with details
    """
    try:
        logger.info(f"Fetching events from URL: {RIVIERA_URL}")
        response = requests.get(RIVIERA_URL, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Response status code: {response.status_code}")
        
        # Save HTML for debugging
        with open('/tmp/riviera_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info("Saved response HTML to /tmp/riviera_response.html")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        events_data = []
        
        # Try different selectors to find the events container
        events_container = None
        
        # Option 1: Look for a div with class containing 'events' or 'conciertos'
        events_container = soup.find('div', class_=lambda c: c and ('events' in c.lower() or 'conciertos' in c.lower()))
        
        # Option 2: Look for the main content area
        if not events_container:
            events_container = soup.find('main', id='main') or soup.find('div', id='content')
        
        # Option 3: Look for any container with event listings
        if not events_container:
            events_container = soup.find('div', class_='elementor-widget-wrap') or soup.find('div', class_='elementor-posts-container')
        
        # Option 4: Just use the body as container
        if not events_container:
            events_container = soup.find('body')
        
        if not events_container:
            logger.error("Could not find any suitable events container on Sala Riviera website")
            return []
        
        logger.info(f"Found events container: {events_container.name} with classes: {events_container.get('class', [])}")
        
        # Try different selectors for event elements
        event_elements = events_container.find_all('article') or events_container.find_all('div', class_=lambda c: c and 'event' in c.lower())
        
        logger.info(f"Found {len(event_elements)} potential event elements")
        
        for i, event in enumerate(event_elements):
            try:
                logger.info(f"Processing event element {i+1}/{len(event_elements)}")
                
                # Debug the event element structure
                event_html = str(event)[:500] + "..." if len(str(event)) > 500 else str(event)
                logger.info(f"Event element HTML snippet: {event_html}")
                
                # Try different selectors for title
                title_element = (
                    event.find('h3', class_='elementor-post__title') or 
                    event.find('h2') or 
                    event.find('h3') or 
                    event.find('h4') or
                    event.find(class_=lambda c: c and 'title' in c.lower())
                )
                
                # If we found a title element but it doesn't have an anchor, look for one
                if title_element and not (hasattr(title_element, 'a') and title_element.a):
                    title_a = title_element.find('a')
                    if title_a:
                        title_element.a = title_a
                
                # If still no title element with link, look for any anchor with title-like text
                if not (title_element and hasattr(title_element, 'a') and title_element.a):
                    title_a = event.find('a', string=lambda s: s and len(s.strip()) > 5)
                    if title_a:
                        title_element = type('obj', (object,), {'a': title_a})
                
                if not (title_element and hasattr(title_element, 'a') and title_element.a):
                    logger.warning(f"Could not find title for event {i+1}")
                    continue
                
                title = title_element.a.text.strip()
                event_url = title_element.a.get('href', '')
                
                logger.info(f"Found event: {title} with URL: {event_url}")
                
                # Extract date - try multiple date formats and selectors
                date_element = (
                    event.find('span', class_='elementor-post-date') or
                    event.find(class_=lambda c: c and 'date' in c.lower()) or
                    event.find('time') or
                    event.find(string=lambda s: s and any(month in s.lower() for month in [
                        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
                    ]))
                )
                
                # Try to extract month and year from the page or URL
                current_year = timezone.now().year
                current_month = timezone.now().month
                
                # Look for month and year in the URL or page title
                page_title = soup.find('title')
                page_title_text = page_title.text if page_title else ""
                
                # Try to find month and year in the URL or page title
                month_year_pattern = re.compile(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)[^\d]*(\d{4})', re.IGNORECASE)
                month_year_match = month_year_pattern.search(RIVIERA_URL) or month_year_pattern.search(page_title_text)
                
                if month_year_match:
                    month_name = month_year_match.group(1).lower()
                    year = int(month_year_match.group(2))
                    
                    # Map Spanish month names to month numbers
                    month_map = {
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                    }
                    
                    if month_name in month_map:
                        current_month = month_map[month_name]
                        current_year = year
                        logger.info(f"Extracted month {current_month} and year {current_year} from URL/title")
                
                event_date = None
                if date_element:
                    date_text = date_element.text.strip() if hasattr(date_element, 'text') else str(date_element).strip()
                    logger.info(f"Found date text: {date_text}")
                    
                    # Check if the date_text is just a day number
                    day_only_pattern = re.compile(r'^\d{1,2}$')
                    if day_only_pattern.match(date_text):
                        # If it's just a day number, use the current month and year
                        try:
                            day = int(date_text)
                            event_date = datetime(current_year, current_month, day, 20, 0)
                            event_date = timezone.make_aware(event_date)
                            logger.info(f"Parsed day-only date as: {event_date}")
                        except (ValueError, OverflowError) as e:
                            logger.warning(f"Error parsing day-only date '{date_text}': {e}")
                            event_date = None
                    else:
                        # Try to parse the full date
                        try:
                            # Example format: "abril 20, 2025"
                            # Convert Spanish month names to English
                            spanish_to_english = {
                                'enero': 'January', 'febrero': 'February', 'marzo': 'March',
                                'abril': 'April', 'mayo': 'May', 'junio': 'June',
                                'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
                                'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
                            }
                            
                            for spanish, english in spanish_to_english.items():
                                if spanish in date_text.lower():
                                    date_text = date_text.lower().replace(spanish, english)
                                    break
                            
                            # Try multiple date formats
                            for date_format in ["%B %d, %Y", "%d %B %Y", "%d/%m/%Y", "%Y-%m-%d"]:
                                try:
                                    event_date = datetime.strptime(date_text, date_format)
                                    break
                                except ValueError:
                                    continue
                            
                            # If we found a date, set time and timezone
                            if event_date:
                                # Set a default time (8:00 PM)
                                event_date = event_date.replace(hour=20, minute=0)
                                event_date = timezone.make_aware(event_date)
                                logger.info(f"Parsed full date: {event_date}")
                        except Exception as e:
                            logger.warning(f"Error parsing full date '{date_text}': {e}")
                            event_date = None
                
                # If we still don't have a date, use a future date
                if not event_date:
                    # Use a future date (30 days from now)
                    event_date = timezone.now() + timezone.timedelta(days=30)
                    logger.warning(f"Could not parse date for event '{title}', using default future date: {event_date}")
                
                # Extract image URL - try multiple selectors
                image_element = (
                    event.find('img') or
                    event.find(class_=lambda c: c and 'image' in c.lower())
                )
                
                image_url = None
                if image_element:
                    # Try different attributes for image URL
                    for attr in ['src', 'data-src', 'data-lazy-src']:
                        if image_element.get(attr):
                            image_url = image_element.get(attr)
                            break
                    
                    if not image_url and image_element.find('img'):
                        for attr in ['src', 'data-src', 'data-lazy-src']:
                            if image_element.find('img').get(attr):
                                image_url = image_element.find('img').get(attr)
                                break
                
                logger.info(f"Image URL: {image_url}")
                
                # Extract description - try multiple selectors
                description_element = (
                    event.find('div', class_='elementor-post__excerpt') or
                    event.find(class_=lambda c: c and 'excerpt' in c.lower()) or
                    event.find(class_=lambda c: c and 'description' in c.lower()) or
                    event.find('p')
                )
                
                description = ""
                if description_element:
                    if description_element.p:
                        description = description_element.p.text.strip()
                    else:
                        description = description_element.text.strip()
                
                logger.info(f"Description: {description[:100]}...")
                
                # Create event data dictionary
                event_data = {
                    'title': title,
                    'date': event_date,
                    'description': description,
                    'image_url': image_url,
                    'ticket_url': event_url,
                    'external_id': f"riviera-{slugify(title)}-{event_date.strftime('%Y-%m-%d')}"
                }
                
                events_data.append(event_data)
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                continue
        
        return events_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching events from Sala Riviera: {e}")
        return []

class RivieraEventSync(EventSyncBase):
    """Sala Riviera event synchronization implementation."""

    def __init__(self):
        super().__init__('riviera')
        self.venue = None

    def sync_events(self):
        """
        Synchronize events from Sala Riviera website to the database.
        
        Returns:
            tuple: (created_count, updated_count, error_message)
        """
        # Get or create the Sala Riviera venue
        self.venue, venue_created = self.create_or_update_venue(VENUE_INFO)
        if not self.venue:
            return 0, 0, "Failed to create/get venue"
        
        if venue_created:
            logger.info(f"Created venue: {self.venue.name}")
        
        # Fetch events from Sala Riviera
        events_data = fetch_riviera_events()
        logger.info(f"Fetched {len(events_data)} events from Sala Riviera website")
        
        for event_data in events_data:
            try:
                # Process event
                event, created = self.create_or_update_event(event_data, self.venue)
                if not event:
                    continue

                # Extract and create artist
                artist_name = self._extract_artist_name(event.title)
                artist_data = {
                    'name': artist_name,
                    'bio': f"Artist performing at {self.venue.name}"
                }
                artist, _ = self.create_or_update_artist(artist_data)
                if artist:
                    event.artists.add(artist)

                logger.info(f"{'Created' if created else 'Updated'} event: {event.title}")
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.error_count += 1
                continue
        
        return self.created_count, self.updated_count, self.error_count if self.error_count > 0 else None

    def _extract_artist_name(self, title):
        """Extract artist name from event title."""
        artist_name = title
        if ' - ' in artist_name:
            artist_name = artist_name.split(' - ')[0].strip()
        elif ' + ' in artist_name:
            artist_name = artist_name.split(' + ')[0].strip()
        elif ' con ' in artist_name.lower():
            artist_name = artist_name.split(' con ')[0].strip()
        return artist_name


def sync_riviera_events():
    """
    Synchronize events from Sala Riviera website to the database.
    Wrapper function for backward compatibility.
    
    Returns:
        tuple: (created_count, updated_count, error_count)
    """
    syncer = RivieraEventSync()
    return syncer.sync_events()


