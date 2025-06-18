"""Core models module for the AI Football Platform.

This module contains base models and core functionality used across the
application. It includes the custom User model, base models with common fields,
and utility models.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel


class BaseModel(models.Model):
    """
    Base model with common fields used across the application.
    Provides tracking for creation and update timestamps, and active status.
    All other models should inherit from this to maintain consistency.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        """Meta options for BaseModel."""

        abstract = True


class User(AbstractUser):
    """
    Extended User model that serves as the central authentication entity.
    Inherits from Django's AbstractUser and adds custom fields.

    Relationships:
    - One-to-One with UserProfile (polymorphic)
    - Used by various models across the system

    Dependencies:
    - Django's AbstractUser
    - Used by all profile models in academies app
    """

    USER_TYPES = (
        ("system_admin", "System Admin"),
        ("academy_admin", "Academy Admin"),
        ("coach", "Coach"),
        ("player", "Player"),
        ("parent", "Parent"),
        ("external_client", "External Client"),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    # language = models.CharField(max_length=2, choices=[('en', 'English'), ('ar', 'Arabic')], default='en')

    class Meta:
        """Meta options for User model."""

        db_table = "auth_user"


class UserProfile(PolymorphicModel, BaseModel):
    """
    Base profile for all user types using polymorphic inheritance.
    This allows for different profile types while maintaining a unified query interface.

    Relationships:
    - One-to-One with User
    - Parent class for all specific profile types (AcademyAdminProfile, CoachProfile, etc.)

    Dependencies:
    - PolymorphicModel from django-polymorphic
    - BaseModel for common fields
    - User model for the one-to-one relationship
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        """Return string representation of the user profile."""
        return f"{self.user.username} - {self.user.user_type}"


# apps/core/models.py (Additional base classes)
class TimestampedModel(models.Model):
    """
    Base model with timestamp fields only.
    Used when only timestamp tracking is needed without the active status.

    Dependencies:
    - None, but provides a foundation for other models
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for TimestampedModel."""

        abstract = True


class SoftDeletableModel(models.Model):
    """
    Base model with soft delete functionality.
    Allows "deleting" records without actually removing them from the database.

    Dependencies:
    - Django's timezone utility for tracking deletion time
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for SoftDeletableModel."""

        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Override the delete method to perform a soft delete instead of hard delete.
        Sets is_deleted flag and records deletion timestamp.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """
        Performs an actual deletion from the database when necessary.
        """
        super().delete()
