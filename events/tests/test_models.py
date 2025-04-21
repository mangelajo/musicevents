from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from events.models import Artist, Event, Venue
import os
from PIL import Image
from io import BytesIO


class ArtistImageTests(TestCase):
    def setUp(self):
        # Create test image
        self.image_data = self._create_test_image()
        self.event_image_data = self._create_test_image(color='blue')
        
        # Create test artist
        self.artist = Artist.objects.create(
            name='Test Artist',
            bio='Test Bio'
        )
        
        # Create test venue
        self.venue = Venue.objects.create(
            name='Test Venue',
            address='123 Test St',
            city='Test City',
            state='Test State',
            zip_code='12345'
        )
        
        # Create test event with image
        self.event = Event.objects.create(
            title='Test Event',
            date=timezone.now(),
            venue=self.venue,
            image=SimpleUploadedFile('event_image.jpg', self.event_image_data)
        )
        self.event.artists.add(self.artist)

    def _create_test_image(self, size=(100, 100), color='red', format='JPEG'):
        """Helper method to create a test image file"""
        image = Image.new('RGB', size, color)
        image_io = BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        return image_io.getvalue()

    def test_artist_with_own_image(self):
        """Test that artist's own image is returned when it exists"""
        # Add image to artist
        self.artist.image = SimpleUploadedFile('artist_image.jpg', self.image_data)
        self.artist.save()
        
        # Check that get_image returns artist's own image
        self.assertEqual(self.artist.get_image, self.artist.image)
        self.assertTrue(os.path.exists(self.artist.image.path))

    def test_artist_without_image_uses_event_image(self):
        """Test that artist uses event image when no own image exists"""
        # Ensure artist has no image
        self.assertFalse(bool(self.artist.image))
        
        # Get image (should get from event)
        image = self.artist.get_image
        
        # Check that image was obtained from event and saved
        self.assertIsNotNone(image)
        self.assertTrue(os.path.exists(self.artist.image.path))
        self.assertTrue(self.artist.image.name.startswith('artists/'))

    def test_artist_without_image_or_event_images(self):
        """Test that None is returned when no images are available"""
        # Create new artist without images
        artist = Artist.objects.create(name='No Image Artist')
        
        # Create event without image
        event = Event.objects.create(
            title='No Image Event',
            date=timezone.now(),
            venue=self.venue
        )
        event.artists.add(artist)
        
        # Check that get_image returns None
        self.assertIsNone(artist.get_image)
        self.assertFalse(bool(artist.image))

    def test_save_event_image_to_artist(self):
        """Test the save_event_image method"""
        # Ensure artist has no image initially
        self.assertFalse(bool(self.artist.image))
        
        # Save event image to artist
        self.artist.save_event_image(self.event)
        
        # Check that image was saved correctly
        self.assertTrue(bool(self.artist.image))
        self.assertTrue(os.path.exists(self.artist.image.path))
        self.assertTrue(self.artist.image.name.startswith('artists/'))

    def test_save_triggers_event_image_copy(self):
        """Test that saving artist without image triggers event image copy"""
        # Create new artist
        artist = Artist.objects.create(name='New Artist')
        
        # Add to event with image
        self.event.artists.add(artist)
        
        # Save artist (should trigger image copy)
        artist.save()
        
        # Check that image was copied
        self.assertTrue(bool(artist.image))
        self.assertTrue(os.path.exists(artist.image.path))

    def tearDown(self):
        # Clean up any created files
        if self.artist.image:
            if os.path.exists(self.artist.image.path):
                os.remove(self.artist.image.path)
        if self.event.image:
            if os.path.exists(self.event.image.path):
                os.remove(self.event.image.path)