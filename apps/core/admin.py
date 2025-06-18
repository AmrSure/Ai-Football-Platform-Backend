"""Core admin module for the AI Football Platform.

This module contains base admin classes and mixins used across the app.
It provides admin interfaces and utility functions for the admin panel.
"""

from django.contrib import admin
from django.utils.html import format_html


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base admin with common configurations for all model admins.

    Provides consistent admin interface for models inheriting from BaseModel.

    Features:
    - Standard list display with id, timestamps, and active status
    - Common filters for active status and timestamps
    - Pagination set to 25 items per page
    - Makes timestamp fields read-only when editing existing objects

    Dependencies:
    - Django's ModelAdmin
    """

    list_display = ["id", "created_at", "updated_at", "is_active"]
    list_filter = ["is_active", "created_at", "updated_at"]
    search_fields = []
    ordering = ["-created_at"]
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")


class AcademyScopedAdmin(BaseModelAdmin):
    """
    Base admin for academy-scoped models.

    Filters querysets based on user's academy permissions.

    Features:
    - Superusers see all objects
    - Academy users only see objects from their academy
    - Other users see no objects

    Dependencies:
    - BaseModelAdmin as parent class
    - User model with profile relationship containing academy
    """

    def get_queryset(self, request):
        """
        Filter queryset based on user's academy access.

        Implements academy-level access control in the admin interface.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by user's academy if applicable
        if hasattr(request.user, "profile") and hasattr(
            request.user.profile, "academy"
        ):
            return qs.filter(academy=request.user.profile.academy)
        return qs.none()


class ImagePreviewMixin:
    """
    Mixin to show image preview in admin.

    Adds a preview column for image fields in the admin list view.

    Features:
    - Displays thumbnail preview of image fields
    - Falls back to "No Image" text when no image is available

    Dependencies:
    - Django's format_html utility
    """

    def image_preview(self, obj):
        """
        Generate HTML for image preview.

        Returns a small thumbnail or "No Image" text.
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;"/>',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Preview"
