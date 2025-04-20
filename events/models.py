from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.text import slugify
import os
from PIL import Image
from io import BytesIO

class Artist(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=False, blank=True, null=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    artists = models.ManyToManyField(Artist, related_name='events')
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    ticket_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="Original image URL from external source")
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True, help_text="Thumbnail version of the image")
    external_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID from external API (e.g., Ticketmaster)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return self.date < timezone.now()
        
    def generate_thumbnail(self, size=(300, 200), quality=85):
        """Generate a thumbnail for the event image"""
        if not self.image:
            self.thumbnail = None
            return

        try:
            # Open the image
            img = Image.open(self.image)

            # Convert to RGB if it's RGBA or P (palette) mode to remove alpha channel
            if img.mode == 'RGBA' or img.mode == 'P':
                img = img.convert('RGB')
            elif img.mode != 'RGB':
                # Handle other modes like L (grayscale) if necessary, or convert non-RGB to RGB
                img = img.convert('RGB')

            # Create a thumbnail
            img.thumbnail(size, Image.LANCZOS)

            # Save the thumbnail to a BytesIO object
            thumb_io = BytesIO()
            # Ensure saving as JPEG
            img.save(thumb_io, format='JPEG', quality=quality, optimize=True)
            thumb_io.seek(0)

            # Get the original filename and create a new filename for the thumbnail
            original_name = os.path.basename(self.image.name)
            name, ext = os.path.splitext(original_name)
            # Ensure the thumbnail name uses .jpg extension
            thumbnail_name = f"thumb_{name}.jpg"

            # Save the thumbnail to the thumbnail field
            # Use save=False as the main model save will handle saving the field
            self.thumbnail.save(thumbnail_name, ContentFile(thumb_io.read()), save=False)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating thumbnail for event {self.title} (Image: {self.image.name}): {e}")
            self.thumbnail = None  # Ensure thumbnail field is cleared on error

    def save(self, *args, **kwargs):
        """Override save to generate thumbnail if image exists"""
        if not self.slug:
            self.slug = slugify(self.title)

        # Skip thumbnail generation if 'skip_thumbnail' is in kwargs
        skip_thumbnail = kwargs.pop('skip_thumbnail', False)
        if skip_thumbnail:
            return super().save(*args, **kwargs)

        # Generate thumbnail if needed
        generate_thumb = False
        if self.image and not self.thumbnail:
            generate_thumb = True
        elif self.pk:
            try:
                old_instance = Event.objects.get(pk=self.pk)
                if old_instance.image != self.image and self.image:
                    generate_thumb = True
            except Event.DoesNotExist:
                if self.image:  # Handle case where instance is being created with image
                    generate_thumb = True

        if generate_thumb:
            self.generate_thumbnail()  # This will set self.thumbnail if successful

        super().save(*args, **kwargs)  # Save the instance with the potentially updated thumbnail field
