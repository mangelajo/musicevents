"""
Django settings loader for music_events_project.
Loads different settings based on the DJANGO_ENV environment variable.
"""

import os

# Get the environment setting, default to 'dev'
env = os.getenv('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *
else:
    from .dev import *