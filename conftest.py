import pytest
from unittest.mock import patch
from events.tests.patches import mock_image_response, mock_fetch_riviera_events

@pytest.fixture(autouse=True)
def patch_image_download():
    """Patch the image download function to use our mock response"""
    with patch('requests.get', mock_image_response), \
         patch('events.utils.riviera_sync.fetch_riviera_events', mock_fetch_riviera_events):
        yield