"""
Admin configuration for the academies app.

This module registers all academy-related models with the Django admin site
and configures their admin interfaces with appropriate display fields, filters,
and search capabilities.
"""

from django.contrib import admin

from apps.core.admin import AcademyScopedAdmin, BaseModelAdmin, ImagePreviewMixin

from .models import (
    Academy,
    AcademyAdminProfile,
    CoachProfile,
    ExternalClientProfile,
    ParentProfile,
    PlayerProfile,
)


@admin.register(Academy)
class AcademyAdmin(ImagePreviewMixin, BaseModelAdmin):
    """
    Admin configuration for Academy model.
    Includes image preview for logo and custom display fields.
    """

    list_display = ["id", "name", "email", "phone", "image_preview", "is_active"]
    list_filter = ["is_active", "created_at", "established_date"]
    search_fields = ["name", "name_ar", "email", "phone"]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "name_ar", "description", "logo", "established_date")},
        ),
        ("Contact Information", {"fields": ("address", "phone", "email", "website")}),
        ("Status", {"fields": ("is_active",)}),
    )
    readonly_fields = ("created_at", "updated_at")

    def image_preview(self, obj):
        """Preview academy logo in admin list view."""
        if obj.logo:
            return super().image_preview(obj)
        return "No Logo"

    image_preview.short_description = "Logo"


@admin.register(AcademyAdminProfile)
class AcademyAdminProfileAdmin(AcademyScopedAdmin):
    """Admin configuration for AcademyAdminProfile model."""

    list_display = ["id", "user", "academy", "position", "is_active"]
    list_filter = ["is_active", "academy", "position"]
    search_fields = ["user__username", "user__email", "position"]
    raw_id_fields = ["user", "academy"]


@admin.register(CoachProfile)
class CoachProfileAdmin(AcademyScopedAdmin):
    """Admin configuration for CoachProfile model."""

    list_display = [
        "id",
        "user",
        "academy",
        "specialization",
        "experience_years",
        "is_active",
    ]
    list_filter = ["is_active", "academy", "specialization", "experience_years"]
    search_fields = ["user__username", "user__email", "specialization"]
    raw_id_fields = ["user", "academy"]


@admin.register(PlayerProfile)
class PlayerProfileAdmin(AcademyScopedAdmin):
    """Admin configuration for PlayerProfile model."""

    list_display = [
        "id",
        "user",
        "academy",
        "jersey_number",
        "position",
        "dominant_foot",
        "is_active",
    ]
    list_filter = ["is_active", "academy", "position", "dominant_foot"]
    search_fields = ["user__username", "user__email", "jersey_number"]
    raw_id_fields = ["user", "academy"]


@admin.register(ParentProfile)
class ParentProfileAdmin(BaseModelAdmin):
    """Admin configuration for ParentProfile model."""

    list_display = ["id", "user", "relationship", "is_active"]
    list_filter = ["is_active", "relationship"]
    search_fields = ["user__username", "user__email"]
    raw_id_fields = ["user"]
    filter_horizontal = ["children"]


@admin.register(ExternalClientProfile)
class ExternalClientProfileAdmin(BaseModelAdmin):
    """Admin configuration for ExternalClientProfile model."""

    list_display = ["id", "user", "organization", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["user__username", "user__email", "organization"]
    raw_id_fields = ["user"]
