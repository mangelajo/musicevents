"""Tests for event synchronization functionality."""
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
from events.utils.sync_base import EventSyncBase
from events.utils.ticketmaster import TicketmasterEventSync
from events.utils.riviera_sync import RivieraEventSync
from events.models import Event, Venue, Artist
from events.tests.patches import mock_image_response, mock_fetch_riviera_events

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

    @patch('events.utils.sync_base.download_and_save_image', return_value=True)
    def test_create_event(self, mock_download):
        """Test event creation."""
        venue, _ = self.sync.create_or_update_venue(self.venue_data)

        event, created = self.sync.create_or_update_event(self.event_data, venue)

        self.assertTrue(created)
        self.assertEqual(event.title, self.event_data['title'])
        self.assertEqual(event.venue, venue)
        self.assertEqual(self.sync.created_count, 1)
        mock_download.assert_called_once()

    @patch('events.utils.sync_base.download_and_save_image', return_value=True)
    def test_update_event(self, mock_download):
        """Test event update."""
        venue, _ = self.sync.create_or_update_venue(self.venue_data)

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
