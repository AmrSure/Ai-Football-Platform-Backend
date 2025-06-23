"""
URL Configuration for the AI Football Platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

        This API provides endpoints for managing football academies, players, coaches, matches, analytics, and more.

        ## Authentication

        The API uses **email-based JWT (JSON Web Token) authentication**. To authenticate:

        1. **Login**: Send a POST request to `/api/v1/auth/login/` with your email and password:
           ```json
           {
             "username": "user@example.com",  // Note: field name is "username" for JWT compatibility
             "password": "your_password"
           }
           ```

        2. **Authorization**: Include the access token in the Authorization header of your requests:
           ```
           Authorization: Bearer <access_token>
           ```

        3. **Token Refresh**: When the access token expires, use the refresh token to get a new one via `/api/v1/auth/refresh/`:
           ```json
           {
             "refresh": "your_refresh_token"
           }
           ```

        ## Important: Email-Based Authentication

        - ✅ **Login Field**: Use `email` address instead of username
        - ✅ **JWT Field Name**: The login endpoint still uses `"username"` field name for JWT compatibility, but expects an email address as the value
        - ✅ **Case Insensitive**: Email lookup is case-insensitive
        - ✅ **Unique Identifier**: Email serves as the unique user identifier

        ## User Registration

        ### External Client Registration (Self-Registration)
        ```json
        POST /api/v1/auth/register/
        {
          "email": "user@example.com",
          "password": "secure_password",
          "password_confirm": "secure_password",
          "first_name": "John",
          "last_name": "Doe",
          "user_type": "external_client",
          "phone": "+1234567890"  // optional
        }
        ```

        ### Academy User Registration (Academy Admin Only)
        ```json
        POST /api/v1/auth/academy/register-user/
        {
          "email": "coach@academy.com",
          "password": "secure_password",
          "first_name": "Jane",
          "last_name": "Smith",
          "user_type": "coach",  // or "player", "parent"
          "academy_id": 1,
          "phone": "+1234567890"  // optional
        }
        ```

        ## User Types & Permissions

        The platform supports different user types with specific permissions:

        - **System Admin**: Full access to all features and system management
        - **Academy Admin**: Manage their academy, register/manage coaches, players, and parents
        - **Coach**: Manage assigned players, create/update matches, view analytics
        - **Player**: View profile, matches, performance analytics
        - **Parent**: View children's profiles, matches, and analytics
        - **External Client**: Book facilities and services, limited access

        ## API Structure

        - **🔐 Authentication**: `/api/v1/auth/` - Login, registration, password management
        - **👥 User Management**:
          - `/api/v1/users/` - System admin user management
          - `/api/v1/academy-users/` - Academy admin user management
        - **🏟️ Academies**: `/api/v1/academies/` - Academy management and profiles
        - **⚽ Players**: `/api/v1/players/` - Player profiles and management
        - **🥅 Matches**: `/api/v1/matches/` - Match scheduling and management
        - **📅 Bookings**: `/api/v1/bookings/` - Facility and service bookings
        - **📊 Analytics**: `/api/v1/analytics/` - Performance analytics and reporting
        - **🔔 Notifications**: `/api/v1/notifications/` - User notifications and messaging

        ## Response Format

        All API responses follow a consistent format:

        **Successful Response:**
        ```json
        {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "user_type": "player",
          "created_at": "2024-01-01T00:00:00Z"
        }
        ```

        **Error Response:**
        ```json
        {
          "error": "Invalid credentials",
          "detail": "No active account found with the given credentials"
        }
        ```

        ## Testing

        For development and testing, you can create test users using the management command:
        ```bash
        python manage.py create_test_user --email admin@test.com --password admin123 --superuser
        ```
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
    # API URLs
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.academies.urls")),
    path("api/v1/", include("apps.players.urls")),
    path("api/v1/", include("apps.matches.urls")),
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.analytics.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    # Internationalization
    path("i18n/", include("django.conf.urls.i18n")),
    # Swagger documentation
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
admin.site.site_header = "Smart Sports Management System"
admin.site.site_title = "Sports Management Admin"
admin.site.index_title = "Welcome to Sports Management System"
