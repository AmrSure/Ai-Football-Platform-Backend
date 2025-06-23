"""Serializers for the notifications app."""

from rest_framework import serializers

from apps.core.serializers import BaseModelSerializer

from .models import Notification


class NotificationSerializer(BaseModelSerializer):
    """Serializer for Notification model."""

    recipient_email = serializers.CharField(source="recipient.email", read_only=True)
    recipient_name = serializers.CharField(
        source="recipient.get_full_name", read_only=True
    )
    time_since_created = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_email",
            "recipient_name",
            "title",
            "message",
            "notification_type",
            "priority",
            "is_read",
            "read_at",
            "metadata",
            "action_url",
            "time_since_created",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "read_at"]

    def get_time_since_created(self, obj):
        """Get human readable time since notification was created."""
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""

    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    read_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    notifications_by_priority = serializers.DictField()
