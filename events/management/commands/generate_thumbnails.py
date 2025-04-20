from django.core.management.base import BaseCommand
from events.models import Event
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate thumbnails for all events with images'

    def handle(self, *args, **options):
        events = Event.objects.filter(image__isnull=False).exclude(image='')
        total = events.count()
        self.stdout.write(f"Found {total} events with images. Generating thumbnails...")
        
        success_count = 0
        error_count = 0
        
        for event in events:
            try:
                if not event.thumbnail:
                    event.generate_thumbnail()
                    event.save()
                    success_count += 1
                    self.stdout.write(f"Generated thumbnail for event: {event.title}")
                else:
                    self.stdout.write(f"Event already has thumbnail: {event.title}")
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"Error generating thumbnail for event {event.id}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Thumbnail generation complete. Success: {success_count}, Errors: {error_count}, Total: {total}"
        ))