"""Models for the notifications app."""

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class Notification(BaseModel):
    """
    Notification model for user notifications.

    Relationships:
    - Many-to-One with User (recipient)

    Dependencies:
    - BaseModel for common fields
    - Django User model for the foreign key relationship
    """

    NOTIFICATION_TYPES = (
        ("booking", "Booking"),
        ("match", "Match"),
        ("academy", "Academy"),
        ("system", "System"),
        ("reminder", "Reminder"),
    )

    PRIORITY_LEVELS = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_LEVELS, default="medium"
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Optional metadata
    metadata = models.JSONField(null=True, blank=True)
    action_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return string representation of the notification."""
        return f"{self.title} - {self.recipient.email}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone

        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
