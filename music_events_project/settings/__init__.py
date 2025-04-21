"""
Django settings loader for music_events_project.
Loads different settings based on the DJANGO_ENV environment variable.
"""

import os
import sys

# Get the environment setting, default to 'dev'
env = os.getenv('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *  # noqa: F403
    sys.modules[__name__].__dict__.update(
        {k: v for k, v in locals().items() if not k.startswith('_')}
    )
else:
    from .dev import *  # noqa: F403
    sys.modules[__name__].__dict__.update(
        {k: v for k, v in locals().items() if not k.startswith('_')}
    )