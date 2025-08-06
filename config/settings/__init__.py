import os

# Load the appropriate settings based on environment
# This allows importing directly from config.settings
env = os.environ.get("DJANGO_ENV", "development")

# Check if DJANGO_SETTINGS_MODULE is explicitly set to production
if "production" in os.environ.get("DJANGO_SETTINGS_MODULE", ""):
    from .production_standalone import *
elif env == "production":
    from .production_standalone import *
elif env == "staging":
    from .staging import *
else:
    from .development import *
