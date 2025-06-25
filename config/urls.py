"""
URL Configuration for the AI Football Platform Backend.

This module defines the main URL routing for the AI Football Platform API.
It includes all app-specific URLs, API documentation, internationalization,
and development-specific configurations.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

URL Structure:
    - /api/v1/ - Main API endpoints for all applications
    - /admin/ - Django admin interface (internationalized)
    - /api/docs/ - Swagger API documentation
    - /api/redoc/ - ReDoc API documentation
    - /i18n/ - Internationalization endpoints
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="AI Football Platform API",
        default_version="v1",
        description="""
        # AI Football Platform API Documentation

A comprehensive REST API for managing football academies, players, coaches, matches, bookings, and analytics.

## 🔐 Authentication

The API uses **JWT (JSON Web Token) authentication** with email-based login.

### Login Process

1. **Obtain Tokens**: Send a POST request to `/api/v1/auth/login/`
           ```json
           {
     "username": "user@example.com",
             "password": "your_password"
           }
           ```

   **Note**: The field name is `username` for JWT compatibility, but provide your email address.

2. **Use Access Token**: Include the token in the Authorization header
           ```
           Authorization: Bearer <access_token>
           ```

3. **Refresh Token**: When access token expires, use `/api/v1/auth/refresh/`
           ```json
           {
             "refresh": "your_refresh_token"
           }
           ```

### Authentication Features

- ✅ **Email-based login** - Use email address instead of username
- ✅ **Case-insensitive** - Email lookup is case-insensitive
- ✅ **JWT tokens** - Secure token-based authentication
- ✅ **Token refresh** - Seamless token renewal

## 👥 User Registration

### External Client Registration (Public)
        ```json
        POST /api/v1/auth/register/
        {
          "email": "user@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
          "first_name": "John",
          "last_name": "Doe",
          "user_type": "external_client",
  "phone": "+1234567890"
        }
        ```

        ### Academy User Registration (Academy Admin Only)
        ```json
        POST /api/v1/auth/academy/register-user/
        {
          "email": "coach@academy.com",
  "password": "secure_password123",
          "first_name": "Jane",
          "last_name": "Smith",
  "user_type": "coach",
          "academy_id": 1,
  "phone": "+1234567890"
        }
        ```

## 🎯 User Types & Permissions

| User Type | Permissions |
|-----------|-------------|
| **System Admin** | Full platform access and system management |
| **Academy Admin** | Manage academy, coaches, players, and parents |
| **Coach** | Manage assigned players, matches, and analytics |
| **Player** | View profile, matches, and performance data |
| **Parent** | View children's profiles and performance |
| **External Client** | Book facilities and services |

## 🛣️ API Endpoints

### Core Services
- **🔐 Authentication** - `/api/v1/auth/` - Login, registration, password management
- **👤 Core** - `/api/v1/core/` - Core platform functionality
- **👥 Users** - `/api/v1/accounts/` - User account management

### Football Management
- **🏟️ Academies** - `/api/v1/academies/` - Academy management and profiles
- **⚽ Players** - `/api/v1/players/` - Player profiles and team management
- **🥅 Matches** - `/api/v1/matches/` - Match scheduling and results

### Services & Analytics
- **📅 Field Management** - `/api/v1/field/` - Field and facility management
- **📅 Field Bookings** - `/api/v1/fieldbooking/` - Field booking and reservations
- **📊 Analytics** - `/api/v1/analytics/` - Performance analytics and reports
- **🔔 Notifications** - `/api/v1/notifications/` - User notifications

## 📝 Response Format

### Successful Response
        ```json
        {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "user_type": "player",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
        }
        ```

### Error Response
        ```json
        {
          "error": "Invalid credentials",
  "detail": "No active account found with the given credentials",
  "status_code": 401
        }
        ```

### Validation Error Response
```json
{
  "email": ["This field is required."],
  "password": ["This field must be at least 8 characters long."]
}
```

## 🧪 Development & Testing

### Create Test Users
        ```bash
# Create superuser
        python manage.py create_test_user --email admin@test.com --password admin123 --superuser

# Create academy admin
python manage.py create_test_user --email academy@test.com --password academy123 --user-type academy_admin

# Create coach
python manage.py create_test_user --email coach@test.com --password coach123 --user-type coach
```

### API Testing
- **Swagger UI**: `/api/docs/` - Interactive API documentation
- **ReDoc**: `/api/redoc/` - Clean API documentation
- **Postman Collection**: Available for comprehensive testing

## 📚 Additional Resources

- **API Versioning**: All endpoints are versioned under `/api/v1/`
- **Rate Limiting**: Applied to prevent abuse
- **CORS**: Configured for cross-origin requests
- **Internationalization**: Multi-language support available
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    validators=["flex", "ssv"],
    generator_class=OpenAPISchemaGenerator,
)

# Base URL patterns (non-internationalized)
urlpatterns = [
    # API URLs - Core functionality
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.academies.urls")),
    path("api/v1/", include("apps.players.urls")),
    path("api/v1/", include("apps.matches.urls")),
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.analytics.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    # Internationalization
    path("i18n/", include("django.conf.urls.i18n")),
    # API Documentation
    path(
        "api/docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

# Add internationalized patterns, including admin
urlpatterns += i18n_patterns(
    # Admin site with i18n support
    path("admin/", admin.site.urls),
    prefix_default_language=False,
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )

    # Debug toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin
admin.site.site_header = "AI Football Platform Admin"
admin.site.site_title = "AI Football Platform"
admin.site.index_title = "Welcome to AI Football Platform Administration"
