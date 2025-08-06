#!/bin/bash

# Cloud Deployment Script for AI Football Platform
# This script is designed for cloud platforms like Railway, Render, etc.

set -e

echo "🚀 Starting AI Football Platform Cloud Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Set proper permissions
print_status "Setting proper permissions..."
chmod 755 logs media staticfiles

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements/production.txt

# Wait for database to be ready (for cloud platforms)
print_status "Waiting for database to be ready..."
python manage.py check --settings=config.settings.production --database default --deploy

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --settings=config.settings.production_standalone

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production_standalone

# Create superuser if it doesn't exist
print_status "Checking for superuser..."
if ! python manage.py shell --settings=config.settings.production_standalone -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found')
    exit(1)
else:
    print('Superuser exists')
    exit(0)
" 2>/dev/null; then
    print_warning "No superuser found. Creating one..."
    python manage.py createsuperuser --settings=config.settings.production_standalone --noinput || true
else
    print_success "Superuser already exists"
fi

# Create system admin user if it doesn't exist
print_status "Checking for system admin user..."
if ! python manage.py shell --settings=config.settings.production_standalone -c "
from apps.core.models import User
if not User.objects.filter(user_type='system_admin').exists():
    print('No system admin found')
    exit(1)
else:
    print('System admin exists')
    exit(0)
" 2>/dev/null; then
    print_warning "No system admin user found. Creating one..."
    python manage.py shell --settings=config.settings.production_standalone -c "
from apps.core.models import User
from apps.academies.models import Academy, AcademyAdminProfile

# Create system admin user
admin_user = User.objects.create_user(
    email='admin@footballplatform.com',
    password='admin123456',
    first_name='System',
    last_name='Administrator',
    user_type='system_admin',
    is_staff=True,
    is_superuser=True
)

# Create default academy
academy = Academy.objects.create(
    name='Default Academy',
    email='info@defaultacademy.com',
    phone='+1234567890',
    address='123 Football Street, City, Country',
    description='Default academy for the platform'
)

# Create academy admin profile
AcademyAdminProfile.objects.create(
    user=admin_user,
    academy=academy,
    position='Director',
    bio='System administrator for the football platform'
)

print('System admin and default academy created successfully')
"
else
    print_success "System admin user already exists"
fi

# Validate Django configuration
print_status "Validating Django configuration..."
python manage.py check --settings=config.settings.production_standalone --deploy

# Test database connection
print_status "Testing database connection..."
python manage.py dbshell --settings=config.settings.production_standalone -c "SELECT 1;" > /dev/null 2>&1

# Create initial data if needed
print_status "Creating initial data..."
python manage.py shell --settings=config.settings.production_standalone -c "
from apps.bookings.models import Field
from apps.academies.models import Academy

# Create sample fields if none exist
if not Field.objects.exists():
    academy = Academy.objects.first()
    if academy:
        Field.objects.create(
            academy=academy,
            name='Main Football Field',
            field_type='football',
            capacity=500,
            hourly_rate=150.00,
            facilities={
                'lights': True,
                'changing_rooms': True,
                'parking': True,
                'seating': True,
                'scoreboard': True
            },
            is_available=True,
            is_active=True
        )
        print('Sample field created')
    else:
        print('No academy found to create sample field')
else:
    print('Fields already exist')
"

print_success "🎉 Cloud deployment setup completed successfully!"

echo ""
echo "📋 Next steps:"
echo "1. Your application is ready to run with:"
echo "   - gunicorn config.wsgi:application --bind 0.0.0.0:\$PORT --workers 4 --timeout 30"
echo "2. Make sure your cloud platform has these environment variables:"
echo "   - DJANGO_SETTINGS_MODULE=config.settings.production"
echo "   - SECRET_KEY"
echo "   - DATABASE_URL"
echo "   - REDIS_URL (optional)"
echo "3. The application will be available at your cloud platform's URL"
echo ""
print_success "Cloud deployment script completed!"
