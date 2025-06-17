# AI Football Platform Backend

A Django REST API backend for managing football academies, players, matches, and analytics.

## Overview

This platform provides a comprehensive solution for football academies to manage their operations, including player registration, match scheduling, facility booking, and performance analytics.

## Features

- **Academy Management**: Create and manage football academies
- **Player Profiles**: Track player information, statistics, and development
- **Match Management**: Schedule matches, record results, and analyze performance
- **Booking System**: Reserve facilities and schedule training sessions
- **Analytics Dashboard**: Visualize player and team performance metrics
- **Notification System**: Keep users informed about important events

## Tech Stack

- **Framework**: Django 5.2 with Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT (JSON Web Tokens)
- **Caching**: Redis
- **Task Queue**: Celery
- **Documentation**: Swagger/OpenAPI

## Project Structure

```
├── apps/
│   ├── core/           # Base functionality and shared components
│   ├── accounts/       # User authentication and profile management
│   ├── academies/      # Football academy management
│   ├── players/        # Player profiles and statistics
│   ├── matches/        # Match scheduling and results tracking
│   ├── bookings/       # Facility booking and reservation system
│   ├── analytics/      # Data analysis and reporting
│   └── notifications/  # User notification system
├── config/             # Project settings and configuration
│   ├── settings/       # Environment-specific settings
│   │   ├── base.py     # Base settings
│   │   ├── development.py # Development settings
│   │   ├── staging.py  # Staging settings
│   │   └── production.py # Production settings
├── requirements/       # Project dependencies
│   ├── base.txt        # Base requirements
│   └── development.txt # Development requirements
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-football-platform-backend.git
   cd ai-football-platform-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/development.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the API at http://127.0.0.1:8000/api/

### Running Tests

```bash
python manage.py test
```

## API Documentation

API documentation is available at `/api/docs/` when the server is running.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Link: [https://github.com/yourusername/ai-football-platform-backend](https://github.com/yourusername/ai-football-platform-backend)
