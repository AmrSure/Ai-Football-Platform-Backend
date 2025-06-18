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

        The API uses JWT (JSON Web Token) authentication. To authenticate:

        1. Obtain a token pair by sending a POST request to `/api/v1/auth/login/` with your username and password
        2. Include the access token in the Authorization header of your requests: `Authorization: Bearer <token>`
        3. When the access token expires, use the refresh token to get a new one via `/api/v1/auth/refresh/`

        ## User Types

        The platform supports different user types with different permissions:

        - **System Admin**: Full access to all features
        - **Academy Admin**: Can manage their academy, coaches, players, and parents
        - **Coach**: Can manage their assigned players and matches
        - **Player**: Can view their profile, matches, and analytics
        - **Parent**: Can view their children's profiles, matches, and analytics
        - **External Client**: Can book facilities and services

        ## API Structure

        - `/api/v1/auth/`: Authentication endpoints
        - `/api/v1/academy-users/`: Academy user management (for academy admins)
        - `/api/v1/academies/`: Academy management
        - `/api/v1/players/`: Player management
        - `/api/v1/matches/`: Match management
        - `/api/v1/bookings/`: Facility booking
        - `/api/v1/analytics/`: Performance analytics
        - `/api/v1/notifications/`: User notifications
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
