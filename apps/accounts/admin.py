from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from apps.core.models import User


class CustomUserAdmin(UserAdmin):
    """
    Custom admin for User model with extended fields and functionality.
    Enhances the default Django UserAdmin with custom fields and filters.
    """

    list_display = [
        "id",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "avatar_preview",
        "is_active",
    ]
    list_filter = ["is_active", "user_type", "is_staff", "is_superuser", "date_joined"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone", "avatar")},
        ),
        ("User Type", {"fields": ("user_type",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "user_type",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    def avatar_preview(self, obj):
        """Display user avatar preview in admin"""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;"/>',
                obj.avatar.url,
            )
        return "No Avatar"

    avatar_preview.short_description = "Avatar"


# Register the custom User admin
admin.site.register(User, CustomUserAdmin)

# Register any additional account-related models here
