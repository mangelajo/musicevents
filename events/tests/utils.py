import os
import threading
import tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from PIL import Image
import socket
import time
from contextlib import contextmanager
from django.conf import settings

# Create a directory for test images
TEST_IMAGES_DIR = os.path.join(tempfile.gettempdir(), 'musicevents_test_images')
os.makedirs(TEST_IMAGES_DIR, exist_ok=True)

# Generate some test images
def create_test_images():
    """Create test images for the HTTP server to serve"""
    images = {}
    
    # Create a few test images with different colors
    colors = ['red', 'blue', 'green', 'yellow', 'purple']
    for i, color in enumerate(colors):
        img_path = os.path.join(TEST_IMAGES_DIR, f'test_image_{i+1}.jpg')
        img = Image.new('RGB', (100, 100), color)
        img.save(img_path)
        images[f'test_image_{i+1}.jpg'] = img_path
    
    return images

# Custom request handler that serves files from our test directory
class TestImageHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=TEST_IMAGES_DIR, **kwargs)
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass

def find_free_port():
    """Find a free port to use for the test server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@contextmanager
def test_image_server():
    """Context manager that starts a test HTTP server for serving images"""
    # Create test images
    images = create_test_images()
    
    # Find a free port
    port = find_free_port()
    
    # Create and start the server
    server = HTTPServer(('localhost', port), TestImageHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(0.5)
    
    try:
        # Return the server URL and image paths
        server_url = f'http://localhost:{port}'
        image_urls = {name: f'{server_url}/{name}' for name in images.keys()}
        yield server_url, image_urls
    finally:
        # Shut down the server
        server.shutdown()
        server.server_close()