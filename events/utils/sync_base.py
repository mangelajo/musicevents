"""
Base classes and utilities for event synchronization.
"""
import logging
from django.utils import timezone
from events.models import Event, Venue, Artist
from .image_utils import download_and_save_image

logger = logging.getLogger(__name__)

class EventSyncBase:
    """Base class for event synchronization from external sources."""
    
    def __init__(self, source_name):
        self.source_name = source_name
        self.created_count = 0
        self.updated_count = 0
        self.error_count = 0

    def sync_events(self):
        """
        Main synchronization method. Should be implemented by subclasses.
        
        Returns:
            tuple: (created_count, updated_count, error_message)
        """
        raise NotImplementedError("Subclasses must implement sync_events()")

    def create_or_update_event(self, event_data, venue):
        """
        Create or update an event based on the provided data.
        
        Args:
            event_data (dict): Event data including title, date, description, etc.
            venue (Venue): The venue object for this event
            
        Returns:
            tuple: (event, created)
        """
        try:
            # Extract common fields
            title = event_data.get('title')
            date = event_data.get('date')
            description = event_data.get('description', '')
            ticket_url = event_data.get('ticket_url', '')
            external_id = event_data.get('external_id')
            image_url = event_data.get('image_url', '')
            ticket_price = event_data.get('ticket_price')

            if not (title and date and external_id):
                logger.warning(f"Skipping event with missing required data: {title}")
                return None, False

            # Create or update event
            event, created = Event.objects.get_or_create(
                external_id=external_id,
                defaults={
                    'title': title,
                    'date': date,
                    'venue': venue,
                    'description': description,
                    'ticket_url': ticket_url,
                    'ticket_price': ticket_price,
                    'image_url': image_url,
                }
            )

            if created:
                self.created_count += 1
                # Download and save image for new events
                if image_url:
                    self._handle_event_image(event, image_url)
            else:
                # Update existing event
                event.title = title
                event.date = date
                event.description = description
                event.ticket_url = ticket_url
                if ticket_price is not None:
                    event.ticket_price = ticket_price

                # Update image if URL has changed
                if image_url and event.image_url != image_url:
                    event.image_url = image_url
                    self._handle_event_image(event, image_url)
                elif not event.image and event.image_url:
                    # Try to download image again if we have a URL but no image
                    self._handle_event_image(event, event.image_url)

                event.save()
                self.updated_count += 1

            return event, created

        except Exception as e:
            logger.error(f"Error processing event {event_data.get('title', 'Unknown')}: {e}")
            self.error_count += 1
            return None, False

    def _handle_event_image(self, event, image_url):
        """Handle downloading and processing event images."""
        if download_and_save_image(image_url, event):
            if event.image:
                event.generate_thumbnail()

    def create_or_update_venue(self, venue_data):
        """
        Create or update a venue based on the provided data.
        
        Args:
            venue_data (dict): Venue data including name, address, etc.
            
        Returns:
            tuple: (venue, created)
        """
        try:
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults=venue_data
            )
            
            if not created:
                # Update existing venue
                for field, value in venue_data.items():
                    if hasattr(venue, field):
                        setattr(venue, field, value)
                venue.save()
            
            return venue, created
        except Exception as e:
            logger.error(f"Error creating/updating venue {venue_data.get('name')}: {e}")
            return None, False

    def create_or_update_artist(self, artist_data):
        """
        Create or update an artist based on the provided data.
        
        Args:
            artist_data (dict): Artist data including name, bio, etc.
            
        Returns:
            tuple: (artist, created)
        """
        try:
            artist, created = Artist.objects.get_or_create(
                name=artist_data['name'],
                defaults=artist_data
            )
            
            if not created:
                # Update existing artist
                for field, value in artist_data.items():
                    if hasattr(artist, field):
                        setattr(artist, field, value)
                artist.save()
            
            return artist, created
        except Exception as e:
            logger.error(f"Error creating/updating artist {artist_data.get('name')}: {e}")
            return None, False