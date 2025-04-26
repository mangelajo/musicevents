"""Patches for tests to avoid external dependencies."""
import os
import tempfile
from PIL import Image
from unittest.mock import patch, MagicMock
from io import BytesIO
from requests import Response
import json

# Create a test image
def create_test_image():
    """Create a test image for mocking image downloads."""
    test_image_path = os.path.join(tempfile.gettempdir(), 'test_image.jpg')
    img = Image.new('RGB', (100, 100), 'red')
    img.save(test_image_path)
    
    with open(test_image_path, 'rb') as f:
        image_data = f.read()
    
    # Clean up
    os.remove(test_image_path)
    
    return image_data

# Mock for requests.get to return a valid image
def mock_image_response(*args, **kwargs):
    """Mock response for image downloads."""
    url = args[0] if args else kwargs.get('url', '')
    
    response = Response()
    response.status_code = 200
    
    # If the URL is for an image, return a test image
    if url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        response._content = create_test_image()
    # If the URL is for Sala Riviera, return a mock HTML response
    elif 'riviera' in url.lower():
        response._content = b"""
        <html>
            <head><title>Sala Riviera - Conciertos</title></head>
            <body>
                <div class="event">
                    <h2>Test Artist - Live in Concert</h2>
                    <p>Date: 01/01/2025</p>
                    <a href="https://salariviera.com/concierto/test-artist-live">Buy Tickets</a>
                    <img src="http://test.com/image.jpg" alt="Event Image">
                </div>
            </body>
        </html>
        """
    # If the URL is for Cafe Berlin, return a mock HTML response
    elif 'cafeberlin' in url.lower():
        response._content = b"""
        <html>
            <head><title>Cafe Berlin - Eventos</title></head>
            <body>
                <div class="event-card">
                    <div class="event-title">Test Event 1</div>
                    <div class="date"><span class="text-raro-700">25 abr</span></div>
                    <a href="/event/1">Details</a>
                </div>
                <div class="event-card">
                    <div class="event-title">Test Event 2</div>
                    <div class="date"><span class="text-raro-700">26 abr</span></div>
                    <a href="/event/2">Details</a>
                </div>
            </body>
        </html>
        """
    # For any other URL, return a generic response
    else:
        response._content = b"<html><body>Mock response</body></html>"
    
    return response

# Mock for the fetch_riviera_events function
def mock_fetch_riviera_events():
    """Mock for the fetch_riviera_events function."""
    return [{
        'title': 'Test Artist - Live in Concert',
        'date': '2025-01-01',
        'description': 'A test concert',
        'image_url': 'http://test.com/image.jpg',
        'ticket_url': 'https://salariviera.com/concierto/test-artist-live',
        'ticket_price': 25.0,
        'external_id': 'riviera-test-artist-live-2025-01-01'
    }]

# Patch decorator for image downloads
def patch_image_downloads(func):
    """Decorator to patch image downloads in tests."""
    @patch('events.utils.image_utils.requests.get', mock_image_response)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
