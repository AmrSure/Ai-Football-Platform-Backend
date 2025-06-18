"""Core serializers module for the AI Football Platform.

This module contains base serializers and serializer mixins used across the
application. It provides consistent API serialization and utility functions for
REST endpoints.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with common fields for all model serializers.

    Provides read-only timestamp fields for consistent API responses.

    Features:
    - Includes created_at and updated_at as read-only fields

    Dependencies:
    - Django REST Framework's ModelSerializer
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        """Meta options for BaseModelSerializer."""

        abstract = True


class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base user serializer for consistent user representation.

    Provides common user fields and computed full_name field.

    Features:
    - Includes basic user fields
    - Adds computed full_name field
    - Sets appropriate read-only fields

    Dependencies:
    - Django REST Framework's ModelSerializer
    - User model from Django's auth system
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        """Meta options for BaseUserSerializer."""

        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
        ]
        read_only_fields = ["id", "user_type"]

    def get_full_name(self, obj):
        """
        Compute full name from first_name and last_name.

        Returns a trimmed string combining both names.
        """
        return f"{obj.first_name} {obj.last_name}".strip()


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer that allows dynamic field inclusion/exclusion.

    Enables API consumers to request only specific fields or exclude certain
    fields.

    Features:
    - Supports 'fields' parameter to include only specific fields
    - Supports 'exclude' parameter to exclude specific fields
    - Maintains all other ModelSerializer functionality

    Usage:
    - Pass 'fields' or 'exclude' as kwargs when instantiating the serializer

    Dependencies:
    - Django REST Framework's ModelSerializer
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with dynamic fields support.

        Processes 'fields' and 'exclude' kwargs to dynamically modify
        serializer fields.
        """
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)
