"""
Custom authentication backends for the AI Football Platform.

This module provides custom authentication backends that extend Django's
default authentication to support email-based login and other custom
authentication methods.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using email.

    This backend allows users to log in using their email address instead of
    username, which is the standard behavior for this platform.

    Features:
    - Authenticate using email and password
    - Case-insensitive email lookup
    - Maintains compatibility with Django's permission system
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using email and password.

        Args:
            request: The request object
            username: The email address (despite the parameter name)
            password: The user's password
            **kwargs: Additional keyword arguments

        Returns:
            User object if authentication is successful, None otherwise
        """
        if username is None:
            username = kwargs.get("email")

        if username is None or password is None:
            return None

        try:
            # Try to find user by email (case-insensitive)
            user = User.objects.get(Q(email__iexact=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None

        # Check password and return user if valid
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """
        Get user by primary key.

        Args:
            user_id: The user's primary key

        Returns:
            User object if found, None otherwise
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
