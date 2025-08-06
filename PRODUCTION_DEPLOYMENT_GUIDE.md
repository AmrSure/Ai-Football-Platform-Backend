# AI Football Platform - Production Deployment Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying the AI Football Platform to production. The platform is designed to be scalable, secure, and maintainable.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements
- **Python**: 3.11+
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Nginx**: 1.18+
- **Docker**: 20.10+ (optional, for containerized deployment)

## 🔧 Installation Methods

### Method 1: Traditional Server Deployment

#### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git curl

# Install Node.js (for frontend if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Step 2: Clone and Setup Project
```bash
# Clone repository
git clone <your-repo-url>
cd Ai-Football-Platform-Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/production.txt
```

#### Step 3: Environment Configuration
```bash
# Copy environment file
cp env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=football_platform
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

#### Step 4: Database Setup
```bash
# Create database
sudo -u postgres psql
CREATE DATABASE football_platform;
CREATE USER football_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE football_platform TO football_user;
\q

# Run migrations
python manage.py migrate --settings=config.settings.production
```

#### Step 5: Static Files and Media
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# Create media directory
mkdir -p media
chmod 755 media
```

#### Step 6: Create Superuser
```bash
python manage.py createsuperuser --settings=config.settings.production
```

#### Step 7: Run Deployment Script
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Method 2: Docker Deployment

#### Step 1: Install Docker and Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Setup Environment
```bash
# Copy environment file
cp env.example .env

# Edit environment variables for Docker
nano .env
```

#### Step 3: Deploy with Docker Compose
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔐 Security Configuration

### SSL/HTTPS Setup

#### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Manual SSL Setup
```bash
# Generate self-signed certificate (for testing)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem
```

### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📊 Monitoring and Logging

### Log Management
```bash
# View application logs
tail -f logs/django.log

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
journalctl -u football-platform -f
```

### Health Checks
```bash
# Application health
curl -f http://yourdomain.com/health/

# Database health
python manage.py check --settings=config.settings.production --database default
```

## 🔄 Maintenance and Updates

### Regular Maintenance Tasks
```bash
# Backup database
pg_dump football_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Update dependencies
pip install -r requirements/production.txt --upgrade

# Run migrations
python manage.py migrate --settings=config.settings.production

# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# Restart services
sudo systemctl restart football-platform
sudo systemctl restart football-platform-celery
sudo systemctl reload nginx
```

### Performance Optimization
```bash
# Database optimization
python manage.py dbshell --settings=config.settings.production
VACUUM ANALYZE;

# Cache warming
python manage.py shell --settings=config.settings.production
from django.core.cache import cache
cache.clear()
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U football_user -d football_platform
```

#### 2. Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connection
redis-cli ping
```

#### 3. Static Files Not Loading
```bash
# Check static files
ls -la staticfiles/

# Recollect static files
python manage.py collectstatic --noinput --settings=config.settings.production
```

#### 4. Email Not Sending
```bash
# Test email configuration
python manage.py shell --settings=config.settings.production
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### Performance Issues

#### High Memory Usage
```bash
# Check memory usage
free -h

# Optimize Gunicorn workers
# Edit gunicorn.conf.py and reduce workers
```

#### Slow Database Queries
```bash
# Enable query logging
# Add to settings: LOGGING['loggers']['django.db']['level'] = 'DEBUG'
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer (HAProxy, Nginx)
- Multiple application servers
- Database read replicas
- Redis clustering

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Use connection pooling
- Implement caching strategies

## 🔧 Configuration Files

### Key Configuration Files
- `config/settings/production.py` - Production Django settings
- `gunicorn.conf.py` - Gunicorn server configuration
- `nginx.conf` - Nginx reverse proxy configuration
- `docker-compose.prod.yml` - Docker services configuration
- `Dockerfile.prod` - Production Docker image

### Environment Variables
See `env.example` for all available environment variables.

## 📞 Support

### Useful Commands
```bash
# Check service status
sudo systemctl status football-platform
sudo systemctl status football-platform-celery
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Restart services
sudo systemctl restart football-platform
sudo systemctl restart football-platform-celery
sudo systemctl reload nginx

# View logs
journalctl -u football-platform -f
tail -f logs/django.log
```

### Monitoring URLs
- **Application**: https://yourdomain.com
- **API Documentation**: https://yourdomain.com/api/v1/swagger/
- **Admin Panel**: https://yourdomain.com/admin/
- **Health Check**: https://yourdomain.com/health/

## 🎯 Next Steps

1. **Set up monitoring**: Configure Sentry for error tracking
2. **Backup strategy**: Implement automated database backups
3. **CI/CD pipeline**: Set up automated deployment
4. **SSL certificate**: Configure Let's Encrypt auto-renewal
5. **Performance monitoring**: Set up application performance monitoring
6. **Security audit**: Regular security assessments

---

**Note**: This guide assumes a Linux server environment. Adjust commands for your specific operating system and requirements.
