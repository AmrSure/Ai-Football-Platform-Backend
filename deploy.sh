#!/bin/bash

# AI Football Platform Production Deployment Script
# This script handles the complete production deployment process

set -e  # Exit on any error

echo "🚀 Starting AI Football Platform Production Deployment..."

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

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please update .env file with your production settings before continuing."
        read -p "Press Enter after updating .env file..."
    else
        print_error ".env.example not found. Please create a .env file with your production settings."
        exit 1
    fi
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

# Check if PostgreSQL is running
print_status "Checking database connection..."
python manage.py check --settings=config.settings.production --database default

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --settings=config.settings.production

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

# Create superuser if it doesn't exist
print_status "Checking for superuser..."
if ! python manage.py shell --settings=config.settings.production -c "
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
    python manage.py createsuperuser --settings=config.settings.production
else
    print_success "Superuser already exists"
fi

# Create system admin user if it doesn't exist
print_status "Checking for system admin user..."
if ! python manage.py shell --settings=config.settings.production -c "
from apps.core.models import User
if not User.objects.filter(user_type='system_admin').exists():
    print('No system admin found')
    exit(1)
else:
    print('System admin exists')
    exit(0)
" 2>/dev/null; then
    print_warning "No system admin user found. Creating one..."
    python manage.py shell --settings=config.settings.production -c "
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
python manage.py check --settings=config.settings.production --deploy

# Test database connection
print_status "Testing database connection..."
python manage.py dbshell --settings=config.settings.production -c "SELECT 1;" > /dev/null 2>&1

# Create initial data if needed
print_status "Creating initial data..."
python manage.py shell --settings=config.settings.production -c "
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

# Set up Celery (if using Redis)
print_status "Setting up Celery..."
if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is running"
    else
        print_warning "Redis is not running. Starting Redis..."
        redis-server --daemonize yes
    fi
else
    print_warning "Redis not found. Please install Redis for Celery support."
fi

# Create systemd service files (optional)
print_status "Creating systemd service files..."
cat > /etc/systemd/system/football-platform.service << EOF
[Unit]
Description=AI Football Platform
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=$(which gunicorn) config.wsgi:application --config gunicorn.conf.py
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/football-platform-celery.service << EOF
[Unit]
Description=AI Football Platform Celery Worker
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=$(which celery) -A config worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
if command -v systemctl >/dev/null 2>&1; then
    print_status "Enabling systemd services..."
    systemctl daemon-reload
    systemctl enable football-platform.service
    systemctl enable football-platform-celery.service
    print_success "Systemd services enabled"
fi

# Create nginx configuration (optional)
print_status "Creating nginx configuration..."
cat > /etc/nginx/sites-available/football-platform << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root $(pwd)/staticfiles;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        root $(pwd);
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
if command -v nginx >/dev/null 2>&1; then
    print_status "Enabling nginx site..."
    ln -sf /etc/nginx/sites-available/football-platform /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    print_success "Nginx configuration applied"
fi

# Final checks
print_status "Running final checks..."
python manage.py check --settings=config.settings.production

print_success "🎉 Deployment completed successfully!"

echo ""
echo "📋 Next steps:"
echo "1. Update your .env file with production settings"
echo "2. Configure your domain in nginx"
echo "3. Set up SSL certificates (Let's Encrypt recommended)"
echo "4. Start the services:"
echo "   - systemctl start football-platform"
echo "   - systemctl start football-platform-celery"
echo "5. Monitor logs:"
echo "   - journalctl -u football-platform -f"
echo "   - tail -f logs/django.log"
echo ""
echo "🌐 Your application should be available at: http://yourdomain.com"
echo "📚 API documentation: http://yourdomain.com/api/v1/swagger/"
echo "🔧 Admin panel: http://yourdomain.com/admin/"
echo ""
print_success "Deployment script completed!"
