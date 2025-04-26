import functools
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
import requests

# filepath: /Users/ajo/work/music_events/events/tests/decorators.py
def create_fake_image_response(format='JPEG', size=(1, 1), color='red'):
    """Creates a mock requests.Response containing a simple fake image."""
    img = Image.new('RGB', size, color=color)
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)

    mock_response = MagicMock(spec=requests.Response)
    mock_response.content = buffer.read()
    mock_response.status_code = 200
    # Mock raise_for_status to do nothing for success codes
    mock_response.raise_for_status.side_effect = None 
    # Ensure stream=True works if needed (though content is pre-loaded here)
    mock_response.iter_content.return_value = iter([mock_response.content]) 

    return mock_response

def mock_download_image(format='JPEG', size=(1, 1), color='blue'):
    """
    Decorator to patch 'events.utils.image_utils._download_image' 
    and return a fake image response.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            fake_response = create_fake_image_response(format=format, size=size, color=color)
            # Patch the target function within the image_utils module
            with patch('events.utils.image_utils._download_image', return_value=fake_response) as mock_download:
                # You can optionally pass the mock into the test function if needed
                # return func(mock_download, *args, **kwargs) 
                return func(*args, **kwargs)
        return wrapper
    return decorator