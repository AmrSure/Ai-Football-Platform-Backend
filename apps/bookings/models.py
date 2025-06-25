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

    def __str__(self):
        """Return string representation of the field."""
        return f"{self.name} - {self.academy.name}"


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

    def save(self, *args, **kwargs):
        """Auto-calculate total_cost before saving."""
        if not self.total_cost:
            self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    def calculate_total_cost(self):
        """Calculate the total cost based on duration and hourly rate."""
        from decimal import Decimal

        if self.start_time and self.end_time and self.field:
            duration_hours = Decimal(str(self.duration_hours))
            return self.field.hourly_rate * duration_hours
        return Decimal("0.00")

    @property
    def duration_hours(self):
        """Calculate booking duration in hours."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600
        return 0

    @property
    def can_cancel(self):
        """Check if booking can be cancelled."""
        from django.utils import timezone

        return self.start_time > timezone.now() and self.status not in [
            "cancelled",
            "completed",
        ]

    @property
    def can_modify(self):
        """Check if booking can be modified."""
        from django.utils import timezone

        return self.start_time > timezone.now() and self.status == "pending"

    def __str__(self):
        """Return string representation of the field booking."""
        return f"{self.field.name} - {self.booked_by.email} - {self.start_time.date()}"

    def clean(self):
        """Validate booking data."""
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("End time must be after start time")

            if self.start_time < timezone.now():
                raise ValidationError("Cannot create booking in the past")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="end_time_after_start_time",
            )
        ]
