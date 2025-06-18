from django.contrib import admin
from django.utils.html import format_html

from apps.core.admin import AcademyScopedAdmin

from .models import Field, FieldBooking


@admin.register(Field)
class FieldAdmin(AcademyScopedAdmin):
    """
    Admin configuration for Field model.
    Manages sports facilities with their properties and availability.
    """

    list_display = [
        "id",
        "name",
        "academy",
        "field_type",
        "capacity",
        "hourly_rate",
        "availability_status",
        "is_active",
    ]
    list_filter = ["is_active", "is_available", "field_type", "academy"]
    search_fields = ["name", "academy__name"]
    raw_id_fields = ["academy"]

    fieldsets = (
        (
            "Field Information",
            {"fields": ("name", "academy", "field_type", "capacity")},
        ),
        ("Booking Details", {"fields": ("hourly_rate", "facilities", "is_available")}),
        ("Status", {"fields": ("is_active",)}),
    )

    def availability_status(self, obj):
        """Display field availability with color indicator"""
        if obj.is_available:
            return format_html('<span style="color: green;">Available</span>')
        return format_html('<span style="color: red;">Not Available</span>')

    availability_status.short_description = "Availability"


@admin.register(FieldBooking)
class FieldBookingAdmin(AcademyScopedAdmin):
    """
    Admin configuration for FieldBooking model.
    Manages scheduling and booking of fields with status tracking.
    """

    list_display = [
        "id",
        "field",
        "booked_by",
        "start_time",
        "end_time",
        "total_cost",
        "status",
        "is_active",
    ]
    list_filter = ["is_active", "status", "field__academy", "start_time"]
    search_fields = ["field__name", "booked_by__username", "booked_by__email"]
    raw_id_fields = ["field", "booked_by", "match"]
    date_hierarchy = "start_time"

    fieldsets = (
        (
            "Booking Information",
            {"fields": ("field", "booked_by", "start_time", "end_time", "total_cost")},
        ),
        ("Status Information", {"fields": ("status", "notes")}),
        ("Match Information", {"fields": ("match",), "classes": ("collapse",)}),
        ("System Information", {"fields": ("is_active",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        """Filter bookings based on academy access"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "profile") and hasattr(
            request.user.profile, "academy"
        ):
            return qs.filter(field__academy=request.user.profile.academy)
        return qs.none()
