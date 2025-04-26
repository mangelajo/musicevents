from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Artist
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch Spotify data for all artists'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if Spotify data already exists',
        )
        parser.add_argument(
            '--artist-id',
            type=int,
            help='Update a specific artist by ID',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        artist_id = options.get('artist_id')
        
        if artist_id:
            try:
                artist = Artist.objects.get(pk=artist_id)
                self.stdout.write(f"Fetching Spotify data for artist: {artist.name}")
                success = artist.fetch_spotify_data(force_update=force)
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Successfully updated Spotify data for {artist.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Could not find Spotify data for {artist.name}"))
            except Artist.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Artist with ID {artist_id} does not exist"))
            return
        
        # Get all artists
        artists = Artist.objects.all()
        total = artists.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING("No artists found in the database"))
            return
            
        self.stdout.write(f"Fetching Spotify data for {total} artists...")
        
        success_count = 0
        fail_count = 0
        
        for i, artist in enumerate(artists, 1):
            self.stdout.write(f"Processing {i}/{total}: {artist.name}")
            
            # Skip if already has data and not forcing update
            if not force and artist.spotify_id and artist.spotify_last_updated:
                # Only update if data is older than 7 days
                days_since_update = (timezone.now() - artist.spotify_last_updated).days
                if days_since_update < 7:
                    self.stdout.write(f"  Skipping {artist.name} - data is recent ({days_since_update} days old)")
                    continue
            
            # Fetch data
            success = artist.fetch_spotify_data(force_update=force)
            
            if success:
                success_count += 1
                self.stdout.write(f"  ✓ Found Spotify data for {artist.name}")
            else:
                fail_count += 1
                self.stdout.write(f"  ✗ Could not find Spotify data for {artist.name}")
        
        self.stdout.write(self.style.SUCCESS(
            f"Completed Spotify data fetch: {success_count} successful, {fail_count} failed"
        ))