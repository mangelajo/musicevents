"""Tests for Café Berlín event scraper."""
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from django.test import TestCase
from django.utils import timezone
from .decorators import mock_download_image
from events.utils.cafeberlin_sync import (
    CafeBerlinEventSync,
    _parse_date_element,
    _get_and_scrape_event_details,
    _scrape_event_card,
    fetch_cafeberlin_events,
)

# Load test HTML fixtures
def load_fixture(filename):
    """Load HTML fixture from file."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()

class TestCafeBerlinSync(TestCase):
    """Test cases for Café Berlín event scraper."""

    def setUp(self):
        """Set up test environment."""
        self.syncer = CafeBerlinEventSync()
        self.mock_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def test_parse_date_element_valid(self):
        """Test parsing a valid date element."""
        html = """
        <div class="date">
            <span class="text-raro-700">25 abr</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        date_element = soup.find('div', class_='date')
        
        with patch('events.utils.cafeberlin_sync.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 1, 1))
            result = _parse_date_element(date_element)
        
        expected = timezone.make_aware(datetime(2025, 4, 25, 20, 0))
        self.assertEqual(result, expected)

    def test_parse_date_element_varias_fechas(self):
        """Test parsing a date element with 'Varias fechas'."""
        html = """
        <div class="date">
            <span class="text-raro-700">Varias fechas</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        date_element = soup.find('div', class_='date')
        
        with patch('events.utils.cafeberlin_sync.timezone.now') as mock_now:
            now = timezone.make_aware(datetime(2025, 1, 1))
            mock_now.return_value = now
            result = _parse_date_element(date_element)
        
        expected = now + timezone.timedelta(days=30)
        self.assertEqual(result, expected)

    def test_parse_date_element_invalid(self):
        """Test parsing an invalid date element."""
        html = """
        <div class="date">
            <span class="text-raro-700">Invalid Date</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        date_element = soup.find('div', class_='date')
        
        with patch('events.utils.cafeberlin_sync.timezone.now') as mock_now:
            now = timezone.make_aware(datetime(2025, 1, 1))
            mock_now.return_value = now
            result = _parse_date_element(date_element)
        
        expected = now + timezone.timedelta(days=30)
        self.assertEqual(result, expected)

    def test_get_and_scrape_event_details_success(self):
        """Test successful event details scraping."""
        mock_response = MagicMock()
        mock_response.text = """
        <div>Descripción del evento</div>
        <div>Test event description</div>
        <source media="(min-width: 992px)" srcset="/high-res-image.jpg">
        """
        mock_response.raise_for_status.return_value = None
        
        with patch('events.utils.cafeberlin_sync.requests.get', return_value=mock_response):
            description, high_res_image = _get_and_scrape_event_details(
                'https://example.com/event', self.mock_headers
            )
        
        self.assertEqual(description, 'Test event description')
        self.assertEqual(high_res_image, 'https:/high-res-image.jpg')

    def test_get_and_scrape_event_details_no_description(self):
        """Test event details scraping with no description."""
        mock_response = MagicMock()
        mock_response.text = """
        <main>Some event content</main>
        """
        mock_response.raise_for_status.return_value = None
        
        with patch('events.utils.cafeberlin_sync.requests.get', return_value=mock_response):
            description, high_res_image = _get_and_scrape_event_details(
                'https://example.com/event', self.mock_headers
            )
        
        self.assertEqual(description, 'Some event content')
        self.assertIsNone(high_res_image)

    def test_scrape_event_card_success(self):
        """Test successful event card scraping."""
        html = """
        <a href="/event/123" class="event-card">
            <div class="event-title">Test Event</div>
            <div class="date">
                <span class="text-raro-700">25 abr</span>
            </div>
            <div class="price">
                <span class="text-raro-700">15,50€</span>
            </div>
            <source media="(min-width: 992px)" srcset="/image.jpg">
        </a>
        """
        soup = BeautifulSoup(html, 'html.parser')
        event_card = soup.find('a', class_='event-card')
        
        # Mock event details response
        mock_response = MagicMock()
        mock_response.text = """
        <div>Descripción del evento</div>
        <div>Test event description</div>
        <source media="(min-width: 992px)" srcset="/high-res-image.jpg">
        """
        mock_response.raise_for_status.return_value = None
        
        with patch('events.utils.cafeberlin_sync.timezone.now') as mock_now, \
             patch('events.utils.cafeberlin_sync.requests.get', return_value=mock_response):
            mock_now.return_value = timezone.make_aware(datetime(2025, 1, 1))
            result = _scrape_event_card(event_card, self.mock_headers)
        
        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['ticket_price'], 15.50)
        self.assertEqual(result['description'], 'Test event description')
        self.assertEqual(result['image_url'], 'https:/high-res-image.jpg')
        self.assertEqual(result['ticket_url'], 'https://cafeberlinentradas.com/event/123')

    def test_scrape_event_card_missing_title(self):
        """Test event card scraping with missing title."""
        html = """
        <a href="/event/123" class="event-card">
            <div class="date">
                <span class="text-raro-700">25 abr</span>
            </div>
        </a>
        """
        soup = BeautifulSoup(html, 'html.parser')
        event_card = soup.find('a', class_='event-card')
        
        result = _scrape_event_card(event_card, self.mock_headers)
        self.assertIsNone(result)

    @patch('events.utils.cafeberlin_sync.requests.get')
    def test_fetch_cafeberlin_events_success(self, mock_get):
        """Test successful events fetching."""
        # Mock main page response
        mock_main_response = MagicMock()
        mock_main_response.text = """
        <a href="/event/1" class="event-card">
            <div class="event-title">Event 1</div>
            <div class="date">
                <span class="text-raro-700">25 abr</span>
            </div>
        </a>
        <a href="/event/2" class="event-card">
            <div class="event-title">Event 2</div>
            <div class="date">
                <span class="text-raro-700">26 abr</span>
            </div>
        </a>
        """
        mock_main_response.raise_for_status.return_value = None
        
        # Mock event details response
        mock_event_response = MagicMock()
        mock_event_response.text = """
        <div>Descripción del evento</div>
        <div>Test event description</div>
        """
        mock_event_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_main_response] + [mock_event_response] * 2
        
        with patch('events.utils.cafeberlin_sync.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 1, 1))
            results = fetch_cafeberlin_events()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Event 1')
        self.assertEqual(results[1]['title'], 'Event 2')


    @mock_download_image(color='green')
    def test_sync_events_success(self):
        """Test successful event synchronization."""
        mock_events = [
            {
                'title': 'Test Event 1',
                'date': timezone.now(),
                'description': 'Description 1',
                'image_url': 'https://example.com/image1.jpg',
                'ticket_url': 'https://example.com/event1',
                'ticket_price': 15.50,
                'external_id': 'cafeberlin-test-event-1-2025-04-25'
            },
            {
                'title': 'Test Event 2',
                'date': timezone.now(),
                'description': 'Description 2',
                'image_url': 'https://example.com/image2.jpg',
                'ticket_url': 'https://example.com/event2',
                'ticket_price': 20.00,
                'external_id': 'cafeberlin-test-event-2-2025-04-26'
            }
        ]
        
        with patch('events.utils.cafeberlin_sync.fetch_cafeberlin_events', return_value=mock_events):
            created, updated, error = self.syncer.sync_events()
        
        self.assertEqual(created, 2)  # Two events should be created
        self.assertEqual(updated, 0)  # No events should be updated
        self.assertIsNone(error)  # No errors should occur