import os
from .base import *  # noqa: F403

# Read environment variables from .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # noqa: F405

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG') # noqa: F405

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default=SECRET_KEY)  # noqa: F405

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://musicevents:musicevents@localhost:5432/musicevents') # noqa: F405
}

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = os.getenv('STATIC_URL', 'static/')
STATIC_ROOT = os.getenv('STATIC_ROOT', str(BASE_DIR / 'staticfiles'))  # noqa: F405

# Media files
MEDIA_URL = os.getenv('MEDIA_URL', 'media/')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', str(BASE_DIR / 'media'))  # noqa: F405

# Security settings
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

MIDDLEWARE += [ # noqa: F405
    'whitenoise.middleware.WhiteNoiseMiddleware',  # or whatever you need
]
