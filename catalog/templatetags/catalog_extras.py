from django import template
from django.conf import settings
import re

register = template.Library()

@register.filter
def get_image_url(image_field):
    """
    Get the correct URL for an image field that might contain either:
    1. A local file path (for ImageField)
    2. A full URL (for external storage like Supabase)
    """
    if not image_field:
        return None
    
    # If it's already a full URL (starts with http/https), return as is
    if isinstance(image_field, str) and (image_field.startswith('http://') or image_field.startswith('https://')):
        return image_field
    
    # If it's an ImageField with a file, return the URL
    if hasattr(image_field, 'url'):
        return image_field.url
    
    # If it's a string that looks like a file path, construct the media URL
    if isinstance(image_field, str) and not image_field.startswith('http'):
        return f"{settings.MEDIA_URL}{image_field}"
    
    return None 