"""
Utility for synchronizing events from Café Berlín website.
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

# URL for Café Berlín events
CAFEBERLIN_URL = "https://cafeberlinentradas.com/es"

# Venue information for Café Berlín
VENUE_INFO = {
    "name": "Café Berlín",
    "address": "Costanilla de los Ángeles, 20",
    "city": "Madrid",
    "state": "Madrid",
    "zip_code": "28013",
    "website": "https://cafeberlinentradas.com/",
    "capacity": 200  # Approximate capacity
}

def fetch_cafeberlin_events():
    """
    Fetch events from Café Berlín website.
    
    Returns:
        list: List of event dictionaries with details
    """
    try:
        logger.info(f"Fetching events from URL: {CAFEBERLIN_URL}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(CAFEBERLIN_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Response status code: {response.status_code}")
        
        # Save HTML for debugging
        with open('/tmp/cafeberlin_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        logger.info("Saved response HTML to /tmp/cafeberlin_response.html")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        events_data = []
        
        # Find all event cards
        event_cards = soup.find_all('a', class_='event-card')
        logger.info(f"Found {len(event_cards)} event cards")
        
        for event_card in event_cards:
            try:
                # Extract event URL
                event_url = event_card.get('href')
                if not event_url.startswith('http'):
                    event_url = f"https://cafeberlinentradas.com{event_url}"
                
                # Extract event title
                title_element = event_card.find('div', class_='event-title')
                if not title_element:
                    continue
                title = title_element.text.strip()
                
                # Extract date
                date_element = event_card.find('div', class_='date')
                event_date = None
                if date_element:
                    date_text = date_element.find('span', class_='text-raro-700').text.strip()
                    if 'Varias' not in date_text:
                        # Parse Spanish date format (e.g., "25 abr")
                        try:
                            day, month = date_text.split()
                            month_map = {
                                'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4,
                                'may': 5, 'jun': 6, 'jul': 7, 'ago': 8,
                                'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
                            }
                            month_num = month_map.get(month.lower())
                            if month_num:
                                # Use current year, adjust if needed
                                year = timezone.now().year
                                # If the date would be in the past, use next year
                                event_date = timezone.make_aware(datetime(year, month_num, int(day), 20, 0))
                                if event_date < timezone.now():
                                    event_date = timezone.make_aware(datetime(year + 1, month_num, int(day), 20, 0))
                        except (ValueError, AttributeError) as e:
                            logger.warning(f"Error parsing date '{date_text}': {e}")
                
                # If no date found, use a future date
                if not event_date:
                    event_date = timezone.now() + timezone.timedelta(days=30)
                    logger.warning(f"Could not parse date for event '{title}', using default future date: {event_date}")
                
                # Extract price
                price_element = event_card.find('div', class_='price')
                price = None
                if price_element:
                    price_text = price_element.find('span', class_='text-raro-700').text.strip()
                    try:
                        price = float(price_text.replace('€', '').replace(',', '.').strip())
                    except (ValueError, AttributeError):
                        logger.warning(f"Could not parse price '{price_text}'")
                
                # Extract image URL
                image_element = event_card.find('source', media='(min-width: 992px)')
                image_url = None
                if image_element:
                    image_url = image_element.get('srcset')
                    if image_url and not image_url.startswith('http'):
                        image_url = f"https:{image_url}"
                
                # Fetch event details page for description
                description = ""
                try:
                    event_response = requests.get(event_url, headers=headers, timeout=30)
                    event_response.raise_for_status()
                    event_soup = BeautifulSoup(event_response.text, 'html.parser')
                    # Find description section
                    description_header = event_soup.find('div', string=re.compile('Descripción del evento'))
                    if description_header:
                        description_element = description_header.find_next('div')
                        if description_element:
                            description = description_element.text.strip()
                    else:
                        # Try to find any text content that might be the description
                        event_info = event_soup.find('main')
                        if event_info:
                            description = event_info.text.strip()
                except Exception as e:
                    logger.warning(f"Error fetching event details from {event_url}: {e}")
                
                # Create event data dictionary
                event_data = {
                    'title': title,
                    'date': event_date,
                    'description': description,
                    'image_url': image_url,
                    'ticket_url': event_url,
                    'ticket_price': price,
                    'external_id': f"cafeberlin-{slugify(title)}-{event_date.strftime('%Y-%m-%d')}"
                }
                
                events_data.append(event_data)
                logger.info(f"Processed event: {title}")
                
            except Exception as e:
                logger.error(f"Error processing event card: {e}")
                continue
        
        return events_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching events from Café Berlín: {e}")
        return []

class CafeBerlinEventSync(EventSyncBase):
    """Café Berlín event synchronization implementation."""

    def __init__(self):
        super().__init__('cafeberlin')
        self.venue = None

    def sync_events(self):
        """
        Synchronize events from Café Berlín website to the database.
        
        Returns:
            tuple: (created_count, updated_count, error_message)
        """
        # Get or create the Café Berlín venue
        self.venue, venue_created = self.create_or_update_venue(VENUE_INFO)
        if not self.venue:
            return 0, 0, "Failed to create/get venue"
        
        if venue_created:
            logger.info(f"Created venue: {self.venue.name}")
        
        # Fetch events from Café Berlín
        events_data = fetch_cafeberlin_events()
        logger.info(f"Fetched {len(events_data)} events from Café Berlín website")
        
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
        # Remove common separators and keep the first part
        separators = [' - ', ' + ', ' con ', ' y ', ' & ', ' | ']
        for sep in separators:
            if sep in artist_name:
                artist_name = artist_name.split(sep)[0].strip()
        return artist_name


def sync_cafeberlin_events():
    """
    Synchronize events from Café Berlín website to the database.
    Wrapper function for backward compatibility.
    
    Returns:
        tuple: (created_count, updated_count, error_count)
    """
    syncer = CafeBerlinEventSync()
    return syncer.sync_events()