# apps/bookings/models.py
from django.db import models

from apps.core.models import BaseModel


class Field(BaseModel):
    """
    Sports field model representing a physical facility that can be booked.
    Fields belong to academies and can be booked for matches or external use.

    Relationships:
    - Many-to-One with Academy in academies app (academy)
    - One-to-Many with FieldBooking (bookings)
    - One-to-Many with Match in matches app (venue)

    Dependencies:
    - BaseModel for common fields
    - Academy from academies app for the foreign key relationship
    """

    FIELD_TYPES = (
        ("football", "Football"),
        ("basketball", "Basketball"),
        ("volleyball", "Volleyball"),
        ("tennis", "Tennis"),
    )

    academy = models.ForeignKey(
        "academies.Academy", on_delete=models.CASCADE, related_name="fields"
    )
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    capacity = models.PositiveIntegerField()
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    facilities = models.JSONField(default=dict)  # lights, changing rooms, etc.
    is_available = models.BooleanField(default=True)


class FieldBooking(BaseModel):
    """
    Field booking model for scheduling field usage.
    Handles both internal academy bookings for matches and external client bookings.

    Relationships:
    - Many-to-One with Field (field)
    - Many-to-One with User in core app (booked_by)
    - One-to-One with Match in matches app (match) - optional for internal bookings

    Dependencies:
    - BaseModel for common fields
    - Field model for the foreign key relationship
    - User from core app for the foreign key relationship
    - Match from matches app for the one-to-one relationship (optional)
    """

    BOOKING_STATUS = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    )

    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="bookings"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default="pending")
    notes = models.TextField(blank=True)

    # For academy internal bookings
    match = models.OneToOneField(
        "matches.Match", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="end_time_after_start_time",
            )
        ]
