import os

# Load the appropriate settings based on environment
# This allows importing directly from config.settings
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'staging':
    from .staging import *
else:
    from .development import *
