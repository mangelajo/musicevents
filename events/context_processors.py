from django.conf import settings

def site_settings(request):
    """
    Add site-wide settings to template context.
    """
    return {
        'SITE_LOGO': settings.SITE_LOGO,
        'SITE_NAME': settings.SITE_NAME,
        'LANGUAGES': settings.LANGUAGES,
    }