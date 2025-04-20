from django.core.management.base import BaseCommand, CommandError
from events.utils.ticketmaster import sync_events_for_city
from django.conf import settings

class Command(BaseCommand):
    help = 'Sync events from Ticketmaster API for a specific city'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str, help='City name to fetch events for')
        parser.add_argument('--state', type=str, help='State code (e.g., CA, NY)', default=None)
        parser.add_argument('--api-key', type=str, help='Ticketmaster API key (optional, defaults to settings.TICKETMASTER_API_KEY)', default=None)

    def handle(self, *args, **options):
        city = options['city']
        state = options['state']
        api_key = options['api_key']
        
        if not api_key:
            api_key = getattr(settings, 'TICKETMASTER_API_KEY', None)
            if not api_key:
                raise CommandError('Ticketmaster API key not provided. Please provide it as an argument or set TICKETMASTER_API_KEY in settings.')
        
        self.stdout.write(self.style.SUCCESS(f'Syncing events for {city}, {state if state else ""}...'))
        
        created, updated, error = sync_events_for_city(city, state, api_key)
        
        if error:
            self.stdout.write(self.style.ERROR(f'Error: {error}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Successfully synced events for {city}'))
        self.stdout.write(f'Created: {created} events')
        self.stdout.write(f'Updated: {updated} events')