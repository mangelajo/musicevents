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
    slug = models.SlugField(unique=False, blank=True, null=True)  # Add this field
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
            return None
            
        # Open the image
        img = Image.open(self.image)
        
        # Convert to RGB if needed
        if img.mode not in ('L', 'RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Create a thumbnail
        img.thumbnail(size, Image.LANCZOS)
        
        # Save the thumbnail to a BytesIO object
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=quality, optimize=True)
        thumb_io.seek(0)
        
        # Get the original filename and create a new filename for the thumbnail
        original_name = os.path.basename(self.image.name)
        name, ext = os.path.splitext(original_name)
        thumbnail_name = f"thumb_{name}.jpg"
        
        # Save the thumbnail to the thumbnail field
        self.thumbnail.save(thumbnail_name, ContentFile(thumb_io.read()), save=False)
        
    def save(self, *args, **kwargs):
        """Override save to generate thumbnail if image exists"""
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Skip thumbnail generation if 'skip_thumbnail' is in kwargs
        skip_thumbnail = kwargs.pop('skip_thumbnail', False)
        if skip_thumbnail:
            return super().save(*args, **kwargs)
            
        # Check if this is a new image or the image has changed
        if self.pk:
            try:
                old_instance = Event.objects.get(pk=self.pk)
                if old_instance.image != self.image and self.image:
                    # Image has changed, generate new thumbnail
                    super().save(*args, **kwargs)  # Save first to ensure image is saved
                    try:
                        self.generate_thumbnail()
                        super().save(*args, **kwargs)  # Save again with thumbnail
                    except Exception as e:
                        # Log error but don't fail the save
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error generating thumbnail for event {self.title}: {e}")
                    return
            except Event.DoesNotExist:
                pass
        
        # For new instances with an image
        is_new_with_image = not self.pk and self.image
        
        # Save the instance first
        super().save(*args, **kwargs)
        
        # Generate thumbnail if needed
        if is_new_with_image or (not self.thumbnail and self.image):
            try:
                self.generate_thumbnail()
                super().save(*args, **kwargs)  # Save again with thumbnail
            except Exception as e:
                # Log error but don't fail the save
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error generating thumbnail for event {self.title}: {e}")
