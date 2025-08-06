# Procfile for AI Football Platform
# This file defines the processes that will be run by the platform

# Web process - runs the Django application with Gunicorn
web: bash start.sh

# Worker process - runs Celery for background tasks
worker: celery -A config worker --loglevel=info

# Beat process - runs Celery Beat for scheduled tasks
beat: celery -A config beat --loglevel=info

# Release process - runs migrations and setup tasks
release: bash deploy-cloud.sh
