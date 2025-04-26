import pytest
from unittest.mock import patch
from .patches import mock_image_response

@pytest.fixture(autouse=True)
def patch_image_download():
    """Patch the image download function to use our mock response"""
    with patch('events.utils.image_utils.requests.get', mock_image_response):
        yield