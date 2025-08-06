#!/bin/bash

# Startup script for AI Football Platform
# This script is designed for cloud platforms like Railway, Render, etc.

set -e

echo "🚀 Starting AI Football Platform..."

# Run the cloud deployment script
bash deploy-cloud.sh

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --timeout ${TIMEOUT:-30} \
    --access-logfile - \
    --error-logfile - \
    --log-level info
