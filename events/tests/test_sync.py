"""Tests for event synchronization functionality."""
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from events.utils.sync_base import EventSyncBase
from events.utils.ticketmaster import TicketmasterEventSync
from events.utils.riviera_sync import RivieraEventSync
from events.models import Event, Venue, Artist
from datetime import datetime
import json
import os

class EventSyncBaseTests(TestCase):
    """Test the base event synchronization functionality."""

    def setUp(self):
        self.sync = EventSyncBase('test')
        self.venue_data = {
            'name': 'Test Venue',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'website': 'http://test.venue'
        }
        self.event_data = {
            'title': 'Test Event',
            'date': timezone.now(),
            'description': 'Test Description',
            'ticket_url': 'http://test.tickets',
            'ticket_price': 25.0,
            'external_id': 'test-123',
            'image_url': 'http://test.com/image.jpg'
        }

    def test_create_venue(self):
        """Test venue creation."""
        venue, created = self.sync.create_or_update_venue(self.venue_data)
        self.assertTrue(created)
        self.assertEqual(venue.name, self.venue_data['name'])
        self.assertEqual(venue.address, self.venue_data['address'])

    def test_update_venue(self):
        """Test venue update."""
        # First create
        venue, _ = self.sync.create_or_update_venue(self.venue_data)
        
        # Then update
        updated_data = self.venue_data.copy()
        updated_data['address'] = '456 New St'
        venue2, created = self.sync.create_or_update_venue(updated_data)
        
        self.assertFalse(created)
        self.assertEqual(venue.id, venue2.id)
        self.assertEqual(venue2.address, '456 New St')

    @patch('events.utils.sync_base.download_and_save_image')
    def test_create_event(self, mock_download):
        """Test event creation."""
        venue, _ = self.sync.create_or_update_venue(self.venue_data)
        mock_download.return_value = True
        
        event, created = self.sync.create_or_update_event(self.event_data, venue)
        
        self.assertTrue(created)
        self.assertEqual(event.title, self.event_data['title'])
        self.assertEqual(event.venue, venue)
        self.assertEqual(self.sync.created_count, 1)
        mock_download.assert_called_once()

    @patch('events.utils.sync_base.download_and_save_image')
    def test_update_event(self, mock_download):
        """Test event update."""
        venue, _ = self.sync.create_or_update_venue(self.venue_data)
        mock_download.return_value = True
        
        # First create
        event, _ = self.sync.create_or_update_event(self.event_data, venue)
        
        # Then update
        updated_data = self.event_data.copy()
        updated_data['description'] = 'Updated description'
        event2, created = self.sync.create_or_update_event(updated_data, venue)
        
        self.assertFalse(created)
        self.assertEqual(event.id, event2.id)
        self.assertEqual(event2.description, 'Updated description')
        self.assertEqual(self.sync.updated_count, 1)

    def test_create_artist(self):
        """Test artist creation."""
        artist_data = {
            'name': 'Test Artist',
            'bio': 'Test Bio'
        }
        artist, created = self.sync.create_or_update_artist(artist_data)
        
        self.assertTrue(created)
        self.assertEqual(artist.name, artist_data['name'])
        self.assertEqual(artist.bio, artist_data['bio'])

    def test_update_artist(self):
        """Test artist update."""
        artist_data = {
            'name': 'Test Artist',
            'bio': 'Test Bio'
        }
        # First create
        artist, _ = self.sync.create_or_update_artist(artist_data)
        
        # Then update
        updated_data = artist_data.copy()
        updated_data['bio'] = 'Updated bio'
        artist2, created = self.sync.create_or_update_artist(updated_data)
        
        self.assertFalse(created)
        self.assertEqual(artist.id, artist2.id)
        self.assertEqual(artist2.bio, 'Updated bio')


class TicketmasterSyncTests(TestCase):
    """Test the Ticketmaster event synchronization."""

    def setUp(self):
        self.sync = TicketmasterEventSync('Test City', 'TS', 'test-api-key')
        self.event_data = {
            'name': 'Test Event',
            'id': 'tm-123',
            'dates': {
                'start': {
                    'dateTime': '2025-04-20T20:00:00Z'
                }
            },
            '_embedded': {
                'venues': [{
                    'name': 'Test Venue',
                    'address': {'line1': '123 Test St'},
                    'city': {'name': 'Test City'},
                    'state': {'stateCode': 'TS'},
                    'postalCode': '12345',
                    'url': 'http://test.venue'
                }],
                'attractions': [{
                    'name': 'Test Artist'
                }]
            },
            'url': 'http://test.tickets',
            'info': 'Test Description',
            'images': [{
                'ratio': '16_9',
                'width': 1024,
                'url': 'http://test.com/image.jpg'
            }],
            'priceRanges': [{
                'min': 25.0
            }]
        }

    def test_extract_venue_data(self):
        """Test venue data extraction from Ticketmaster data."""
        venue_data = self.sync._extract_venue_data(self.event_data)
        self.assertEqual(venue_data['name'], 'Test Venue')
        self.assertEqual(venue_data['address'], '123 Test St')
        self.assertEqual(venue_data['city'], 'Test City')
        self.assertEqual(venue_data['state'], 'TS')

    def test_extract_event_data(self):
        """Test event data extraction from Ticketmaster data."""
        venue, _ = self.sync.create_or_update_venue(self.sync._extract_venue_data(self.event_data))
        event_data = self.sync._extract_event_data(self.event_data, venue)
        
        self.assertEqual(event_data['title'], 'Test Event')
        self.assertEqual(event_data['external_id'], 'tm-123')
        self.assertEqual(event_data['ticket_price'], 25.0)
        self.assertEqual(event_data['image_url'], 'http://test.com/image.jpg')

    def test_parse_event_date(self):
        """Test event date parsing."""
        date = self.sync._parse_event_date(self.event_data)
        self.assertEqual(date.year, 2025)
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 20)

    def test_get_best_image_url(self):
        """Test image URL selection."""
        url = self.sync._get_best_image_url(self.event_data)
        self.assertEqual(url, 'http://test.com/image.jpg')

    def test_extract_artist_names(self):
        """Test artist name extraction."""
        names = self.sync._extract_artist_names(self.event_data)
        self.assertEqual(names, ['Test Artist'])

    @patch('events.utils.ticketmaster.fetch_events_for_city')
    def test_sync_events(self, mock_fetch):
        """Test full event synchronization."""
        mock_fetch.return_value = {
            '_embedded': {
                'events': [self.event_data]
            }
        }
        
        created, updated, error = self.sync.sync_events()
        
        self.assertEqual(created, 1)
        self.assertEqual(updated, 0)
        self.assertIsNone(error)
        
        # Verify event was created
        event = Event.objects.get(external_id='tm-123')
        self.assertEqual(event.title, 'Test Event')
        
        # Verify venue was created
        venue = Venue.objects.get(name='Test Venue')
        self.assertEqual(venue.city, 'Test City')
        
        # Verify artist was created
        artist = Artist.objects.get(name='Test Artist')
        self.assertTrue(artist in event.artists.all())


class RivieraSyncTests(TestCase):
    """Test the Riviera event synchronization."""

    def setUp(self):
        self.sync = RivieraEventSync()
        self.event_data = {
            'title': 'Test Artist - Live in Concert',
            'date': timezone.now(),
            'description': 'Test Description',
            'ticket_url': 'http://test.tickets',
            'external_id': 'riviera-test-artist-2025-04-20',
            'image_url': 'http://test.com/image.jpg'
        }

    def test_extract_artist_name(self):
        """Test artist name extraction from event title."""
        # Test with hyphen
        self.assertEqual(
            self.sync._extract_artist_name('Test Artist - Live in Concert'),
            'Test Artist'
        )
        
        # Test with plus
        self.assertEqual(
            self.sync._extract_artist_name('Artist One + Artist Two'),
            'Artist One'
        )
        
        # Test with 'con'
        self.assertEqual(
            self.sync._extract_artist_name('Main Artist con Guest Artist'),
            'Main Artist'
        )

    @patch('events.utils.riviera_sync.fetch_riviera_events')
    def test_sync_events(self, mock_fetch):
        """Test full event synchronization."""
        mock_fetch.return_value = [self.event_data]
        
        created, updated, error = self.sync.sync_events()
        
        self.assertEqual(created, 1)
        self.assertEqual(updated, 0)
        self.assertIsNone(error)
        
        # Verify event was created
        event = Event.objects.get(external_id=self.event_data['external_id'])
        self.assertEqual(event.title, self.event_data['title'])
        
        # Verify venue was created
        venue = Venue.objects.get(name='La Riviera')
        self.assertEqual(venue.city, 'Madrid')
        
        # Verify artist was created
        artist = Artist.objects.get(name='Test Artist')
        self.assertTrue(artist in event.artists.all())