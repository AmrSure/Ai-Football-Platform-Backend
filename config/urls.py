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
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="AI Football Platform API",
        default_version="v1",
        description="",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
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

# Add i18n patterns for admin
urlpatterns += i18n_patterns(
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
