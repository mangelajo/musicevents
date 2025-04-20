from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Artist, Venue, Event
import datetime
import random

class Command(BaseCommand):
    help = 'Creates sample data for the Music Events application'

    def handle(self, *args, **kwargs):
        # Create artists
        artists = [
            {
                'name': 'The Melodic Minds',
                'bio': 'A four-piece indie rock band known for their catchy melodies and thoughtful lyrics.',
                'website': 'https://example.com/melodicminds',
            },
            {
                'name': 'Electronic Dreams',
                'bio': 'Electronic music producer creating atmospheric soundscapes and danceable beats.',
                'website': 'https://example.com/electronicdreams',
            },
            {
                'name': 'Jazz Collective',
                'bio': 'A rotating group of jazz musicians pushing the boundaries of contemporary jazz.',
                'website': 'https://example.com/jazzcollective',
            },
            {
                'name': 'Acoustic Harmony',
                'bio': 'Folk duo with beautiful harmonies and storytelling through song.',
                'website': 'https://example.com/acousticharmony',
            },
            {
                'name': 'The Beat Makers',
                'bio': 'Hip-hop group with powerful lyrics and innovative production.',
                'website': 'https://example.com/beatmakers',
            },
        ]

        # Create venues
        venues = [
            {
                'name': 'The Sound Stage',
                'address': '123 Music Ave',
                'city': 'Nashville',
                'state': 'TN',
                'zip_code': '37203',
                'website': 'https://example.com/soundstage',
                'capacity': 500,
            },
            {
                'name': 'Harmony Hall',
                'address': '456 Melody Lane',
                'city': 'Austin',
                'state': 'TX',
                'zip_code': '78701',
                'website': 'https://example.com/harmonyhall',
                'capacity': 1200,
            },
            {
                'name': 'The Jazz Cellar',
                'address': '789 Blues St',
                'city': 'New Orleans',
                'state': 'LA',
                'zip_code': '70116',
                'website': 'https://example.com/jazzcellar',
                'capacity': 150,
            },
            {
                'name': 'Rock Arena',
                'address': '321 Guitar Rd',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90028',
                'website': 'https://example.com/rockarena',
                'capacity': 5000,
            },
            {
                'name': 'Acoustic Cafe',
                'address': '555 Folk Way',
                'city': 'Portland',
                'state': 'OR',
                'zip_code': '97205',
                'website': 'https://example.com/acousticcafe',
                'capacity': 75,
            },
        ]

        # Create events
        events = [
            {
                'title': 'Summer Music Festival',
                'description': 'A weekend of amazing music across multiple genres. Food vendors, art installations, and more!',
                'date': timezone.now() + datetime.timedelta(days=30),
                'venue_index': 3,  # Rock Arena
                'artist_indices': [0, 1, 4],  # Multiple artists
                'ticket_price': 75.00,
                'ticket_url': 'https://example.com/tickets/summerfest',
            },
            {
                'title': 'Jazz Night',
                'description': 'An intimate evening of jazz standards and new compositions.',
                'date': timezone.now() + datetime.timedelta(days=7),
                'venue_index': 2,  # The Jazz Cellar
                'artist_indices': [2],  # Jazz Collective
                'ticket_price': 25.00,
                'ticket_url': 'https://example.com/tickets/jazznight',
            },
            {
                'title': 'Acoustic Sessions',
                'description': 'Unplugged performances in a cozy setting.',
                'date': timezone.now() + datetime.timedelta(days=14),
                'venue_index': 4,  # Acoustic Cafe
                'artist_indices': [3],  # Acoustic Harmony
                'ticket_price': 15.00,
                'ticket_url': 'https://example.com/tickets/acoustic',
            },
            {
                'title': 'Electronic Music Showcase',
                'description': 'A night of cutting-edge electronic music with stunning visuals.',
                'date': timezone.now() + datetime.timedelta(days=21),
                'venue_index': 0,  # The Sound Stage
                'artist_indices': [1],  # Electronic Dreams
                'ticket_price': 30.00,
                'ticket_url': 'https://example.com/tickets/electronic',
            },
            {
                'title': 'Indie Rock Night',
                'description': 'Featuring up-and-coming indie rock bands.',
                'date': timezone.now() + datetime.timedelta(days=10),
                'venue_index': 1,  # Harmony Hall
                'artist_indices': [0],  # The Melodic Minds
                'ticket_price': 20.00,
                'ticket_url': 'https://example.com/tickets/indierock',
            },
            {
                'title': 'Hip-Hop Showcase',
                'description': 'Celebrating the art of hip-hop with performances, DJs, and breakdancing.',
                'date': timezone.now() + datetime.timedelta(days=17),
                'venue_index': 0,  # The Sound Stage
                'artist_indices': [4],  # The Beat Makers
                'ticket_price': 25.00,
                'ticket_url': 'https://example.com/tickets/hiphop',
            },
            {
                'title': 'Music Industry Conference',
                'description': 'Panels, workshops, and networking for music industry professionals.',
                'date': timezone.now() + datetime.timedelta(days=45),
                'venue_index': 1,  # Harmony Hall
                'artist_indices': [],  # No artists
                'ticket_price': 150.00,
                'ticket_url': 'https://example.com/tickets/conference',
            },
            # Past events
            {
                'title': 'New Year\'s Eve Bash',
                'description': 'Ring in the new year with live music and celebration.',
                'date': timezone.now() - datetime.timedelta(days=100),
                'venue_index': 3,  # Rock Arena
                'artist_indices': [0, 1, 2, 3, 4],  # All artists
                'ticket_price': 100.00,
                'ticket_url': '',
            },
            {
                'title': 'Spring Concert Series',
                'description': 'A series of concerts celebrating the arrival of spring.',
                'date': timezone.now() - datetime.timedelta(days=60),
                'venue_index': 2,  # The Jazz Cellar
                'artist_indices': [2, 3],  # Jazz Collective and Acoustic Harmony
                'ticket_price': 35.00,
                'ticket_url': '',
            },
        ]

        # Create artist objects
        artist_objects = []
        for artist_data in artists:
            artist, created = Artist.objects.get_or_create(
                name=artist_data['name'],
                defaults={
                    'bio': artist_data['bio'],
                    'website': artist_data['website'],
                }
            )
            artist_objects.append(artist)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created artist: {artist.name}'))
            else:
                self.stdout.write(f'Artist already exists: {artist.name}')

        # Create venue objects
        venue_objects = []
        for venue_data in venues:
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults={
                    'address': venue_data['address'],
                    'city': venue_data['city'],
                    'state': venue_data['state'],
                    'zip_code': venue_data['zip_code'],
                    'website': venue_data['website'],
                    'capacity': venue_data['capacity'],
                }
            )
            venue_objects.append(venue)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created venue: {venue.name}'))
            else:
                self.stdout.write(f'Venue already exists: {venue.name}')

        # Create event objects
        for event_data in events:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                date=event_data['date'],
                defaults={
                    'description': event_data['description'],
                    'venue': venue_objects[event_data['venue_index']],
                    'ticket_price': event_data['ticket_price'],
                    'ticket_url': event_data['ticket_url'],
                }
            )
            
            # Add artists to the event
            if created:
                for artist_index in event_data['artist_indices']:
                    event.artists.add(artist_objects[artist_index])
                self.stdout.write(self.style.SUCCESS(f'Created event: {event.title}'))
            else:
                self.stdout.write(f'Event already exists: {event.title}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))