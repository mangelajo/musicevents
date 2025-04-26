"""Patches for tests to avoid external dependencies."""
import os
import tempfile
from PIL import Image
from unittest.mock import patch
from io import BytesIO
from requests import Response

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
    response = Response()
    response.status_code = 200
    response._content = create_test_image()
    return response

# Patch decorator for image downloads
def patch_image_downloads(func):
    """Decorator to patch image downloads in tests."""
    @patch('events.utils.image_utils.requests.get', mock_image_response)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper