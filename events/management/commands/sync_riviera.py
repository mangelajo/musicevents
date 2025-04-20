from django.core.management.base import BaseCommand
from events.utils.riviera_sync import sync_riviera_events
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Synchronize events from Sala Riviera website'

    def handle(self, *args, **options):
        self.stdout.write("Starting Sala Riviera events synchronization...")
        
        created, updated, errors = sync_riviera_events()
        
        self.stdout.write(self.style.SUCCESS(
            f"Sala Riviera synchronization complete. "
            f"Created: {created}, Updated: {updated}, Errors: {errors}"
        ))