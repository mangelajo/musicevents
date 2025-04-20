from django.core.management.base import BaseCommand
from events.models import Event
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io
import random

class Command(BaseCommand):
    help = 'Generates and adds sample images to events'

    def handle(self, *args, **kwargs):
        # Get all events
        events = Event.objects.all()
        
        # Generate and add images to events
        for event in events:
            # Skip if event already has an image
            if event.image:
                self.stdout.write(f'Event {event.title} already has an image, skipping')
                continue
                
            # Generate a random color image
            img = self.generate_random_image(800, 600)
            
            # Convert image to bytes
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)
            
            # Create a unique filename
            filename = f"event_{event.id}_{random.randint(1000, 9999)}.jpg"
            
            # Save the image to the event
            event.image.save(filename, ContentFile(img_io.getvalue()), save=True)
            
            # Generate thumbnail
            event.generate_thumbnail()
            event.save()
            
            self.stdout.write(self.style.SUCCESS(f'Added image to event: {event.title}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample images to events'))
    
    def generate_random_image(self, width, height):
        """Generate a random colored image with text"""
        # Create a new image with a random background color
        bg_color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add some random shapes
        for _ in range(5):
            shape_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            x1 = random.randint(0, width - 100)
            y1 = random.randint(0, height - 100)
            x2 = x1 + random.randint(50, 100)
            y2 = y1 + random.randint(50, 100)
            
            # Draw a rectangle
            draw.rectangle([x1, y1, x2, y2], fill=shape_color)
        
        return img