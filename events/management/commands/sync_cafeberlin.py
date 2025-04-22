"""
Management command to synchronize events from Café Berlín website.
"""
from django.core.management.base import BaseCommand
from events.utils.cafeberlin_sync import sync_cafeberlin_events

class Command(BaseCommand):
    help = 'Synchronize events from Café Berlín website'

    def handle(self, *args, **options):
        created, updated, error_count = sync_cafeberlin_events()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synchronized Café Berlín events. '
                f'Created: {created}, Updated: {updated}'
                + (f', Errors: {error_count}' if error_count else '')
            )
        )