from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Development database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

# Add debug toolbar for development
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Media files served by Django in development
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
