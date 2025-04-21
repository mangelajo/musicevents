from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

# Disable django-q for testing
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_q']  # noqa: F405

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p(fny*1)j=!x=xp1%ga+7nk2y98s7(814q@k9*t-=6g9@fgzap'