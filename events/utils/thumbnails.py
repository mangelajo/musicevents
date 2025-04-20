import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

def generate_thumbnail(image_field, size=(300, 200), format='JPEG', quality=85, prefix='thumb_'):
    """
    Generate a thumbnail for an ImageField
    
    Args:
        image_field: The ImageField to generate a thumbnail for
        size: Tuple of (width, height) for the thumbnail
        format: Image format (JPEG, PNG, etc.)
        quality: Image quality (1-100)
        prefix: Prefix for the thumbnail filename
        
    Returns:
        ContentFile: A ContentFile containing the thumbnail
    """
    if not image_field:
        return None
        
    # Open the image using PIL
    img = Image.open(image_field)
    
    # Convert to RGB if needed (for PNG with transparency)
    if img.mode not in ('L', 'RGB', 'RGBA'):
        img = img.convert('RGB')
    
    # Create a thumbnail
    img.thumbnail(size, Image.LANCZOS)
    
    # Save the thumbnail to a BytesIO object
    thumb_io = BytesIO()
    if format.upper() == 'JPEG':
        img.save(thumb_io, format=format, quality=quality, optimize=True)
    else:
        img.save(thumb_io, format=format, optimize=True)
    thumb_io.seek(0)
    
    # Get the original filename and create a new filename for the thumbnail
    original_name = os.path.basename(image_field.name)
    name, ext = os.path.splitext(original_name)
    thumbnail_name = f"{prefix}{name}{ext}"
    
    # Return a ContentFile with the thumbnail
    return ContentFile(thumb_io.read(), name=thumbnail_name)

def get_thumbnail_path(image_field, size=(300, 200), format='JPEG', prefix='thumb_'):
    """
    Get the path to a thumbnail for an ImageField
    
    Args:
        image_field: The ImageField to get a thumbnail path for
        size: Tuple of (width, height) for the thumbnail
        format: Image format (JPEG, PNG, etc.)
        prefix: Prefix for the thumbnail filename
        
    Returns:
        str: Path to the thumbnail
    """
    if not image_field:
        return None
        
    # Get the original filename and create a new filename for the thumbnail
    original_name = os.path.basename(image_field.name)
    name, ext = os.path.splitext(original_name)
    thumbnail_name = f"{prefix}{name}{ext}"
    
    # Get the directory of the original image
    directory = os.path.dirname(image_field.name)
    
    # Return the path to the thumbnail
    return os.path.join(directory, thumbnail_name)