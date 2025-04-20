import requests
import logging
import os
from django.core.files.base import ContentFile
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

def download_and_save_image(url, model_instance, field_name='image'):
    """
    Download an image from a URL, convert it to RGB if necessary,
    and save it to a model instance's ImageField.

    Args:
        url (str): URL of the image to download
        model_instance: Django model instance to save the image to
        field_name (str): Name of the ImageField on the model

    Returns:
        bool: True if successful, False otherwise
    """
    if not url:
        logger.warning("No URL provided for image download.")
        return False

    try:
        # Get the image file name from the URL
        parsed_url = urlparse(url)
        original_name = os.path.basename(parsed_url.path)
        name, ext = os.path.splitext(original_name)
        # Ensure the saved image has a standard extension like .jpg
        image_name = f"{name}.jpg"

        # Download the image
        response = requests.get(url, stream=True, timeout=10) # Added timeout
        response.raise_for_status()

        # Read image into memory
        image_data = BytesIO(response.content)
        img = Image.open(image_data)

        # Convert to RGB if necessary
        if img.mode == 'RGBA' or img.mode == 'P':
            logger.info(f"Converting image from {img.mode} to RGB: {url}")
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            logger.info(f"Converting image from {img.mode} to RGB: {url}")
            img = img.convert('RGB')


        # Save the converted image to a BytesIO object in JPEG format
        output_io = BytesIO()
        img.save(output_io, format='JPEG', quality=85, optimize=True) # Save as JPEG
        output_io.seek(0)

        # Get the model's field
        field = getattr(model_instance, field_name)

        # Save the file content to the field
        # Use ContentFile to save from memory buffer
        field.save(image_name, ContentFile(output_io.read()), save=False)

        # Save the model instance (this should trigger the thumbnail generation if needed)
        # Pass skip_thumbnail=False or remove it if your save method handles it
        model_instance.save()

        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image from {url}: {e}")
        return False
    except IOError as e:
        logger.error(f"Error processing image from {url} (PIL error): {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing image from {url}: {e}")
        return False
    finally:
        # Clean up temp file if it was created (though we moved away from NamedTemporaryFile)
        # This block might not be needed anymore if not using tempfile on disk
        pass