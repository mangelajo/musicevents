import os
import tempfile
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from events.models import Artist, Event, Venue
from django.utils import timezone
from unittest.mock import patch

class TestImageServer(TestCase):
    """Test the image server functionality"""
    
    def setUp(self):
        """Set up test environment with test images"""
        # Create a test image
        self.test_image_path = os.path.join(tempfile.gettempdir(), 'test_image.jpg')
        img = Image.new('RGB', (100, 100), 'red')
        img.save(self.test_image_path)
        
        # Create a test venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            address='123 Test St',
            city='Test City',
            state='Test State',
            zip_code='12345'
        )
    
    def test_image_upload_for_artist(self):
        """Test that we can upload an image for an artist"""
        # Create a test artist
        artist = Artist.objects.create(name="Test Artist", bio="Test Bio")
        
        # Read the test image
        with open(self.test_image_path, 'rb') as f:
            image_data = f.read()
        
        # Create a SimpleUploadedFile
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_data,
            content_type='image/jpeg'
        )
        
        # Set the image
        artist.image = image_file
        artist.save()
        
        # Verify the image was saved
        self.assertTrue(artist.image)
        self.assertTrue(os.path.exists(artist.image.path))
        
        # Clean up
        artist.image.delete()
    
    def test_image_upload_for_event(self):
        """Test that we can upload an image for an event"""
        # Create a test event
        event = Event.objects.create(
            title='Test Event',
            date=timezone.now(),
            venue=self.venue
        )
        
        # Read the test image
        with open(self.test_image_path, 'rb') as f:
            image_data = f.read()
        
        # Create a SimpleUploadedFile
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_data,
            content_type='image/jpeg'
        )
        
        # Set the image
        event.image = image_file
        event.save()
        
        # Verify the image was saved
        self.assertTrue(event.image)
        self.assertTrue(os.path.exists(event.image.path))
        
        # Clean up
        event.image.delete()
    
    @patch('events.utils.image_utils.requests.get')
    def test_download_and_save_image(self, mock_get):
        """Test the download_and_save_image function with a mocked response"""
        from events.utils.image_utils import download_and_save_image
        from requests import Response
        from io import BytesIO
        
        # Create a test artist
        artist = Artist.objects.create(name="Test Artist", bio="Test Bio")
        
        # Read the test image
        with open(self.test_image_path, 'rb') as f:
            image_data = f.read()
        
        # Create a mock response
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = image_data
        mock_get.return_value = mock_response
        
        # Try to download an image
        result = download_and_save_image("https://example.com/image.jpg", artist)
        
        # Verify the download was successful
        self.assertTrue(result)
        self.assertTrue(artist.image)
        
        # Verify the image was saved
        self.assertTrue(artist.image.name.endswith('.jpg'))
        
        # Clean up
        artist.image.delete()
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove the test image
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)