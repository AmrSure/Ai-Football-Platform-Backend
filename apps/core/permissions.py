"""Core permissions module for the AI Football Platform.

This module contains permission classes to control access to API endpoints.
It provides role-based and object-level permissions for the REST API.
"""

from rest_framework import permissions


class BasePermission(permissions.BasePermission):
    """Base permission class with common methods."""

    def has_academy_access(self, user, academy):
        """
        Check if user has access to academy.

        Args:
            user: The user requesting access
            academy: The academy to check access for

        Returns:
            bool: True if user has access, False otherwise
        """
        if user.user_type == "system_admin":
            return True
        if hasattr(user, "profile") and hasattr(user.profile, "academy"):
            return user.profile.academy == academy
        return False


class IsSystemAdmin(permissions.BasePermission):
    """Permission for system admins only."""

    def has_permission(self, request, view):
        """
        Check if user is a system admin.

        Returns:
            bool: True if user is authenticated and a system admin
        """
        return (
            request.user.is_authenticated and request.user.user_type == "system_admin"
        )


class IsAcademyAdmin(permissions.BasePermission):
    """Permission for academy admins."""

    def has_permission(self, request, view):
        """
        Check if user is an academy admin.

        Returns:
            bool: True if user is authenticated and an academy admin
        """
        return (
            request.user.is_authenticated and request.user.user_type == "academy_admin"
        )


class IsCoach(permissions.BasePermission):
    """Permission for coaches."""

    def has_permission(self, request, view):
        """
        Check if user is a coach.

        Returns:
            bool: True if user is authenticated and a coach
        """
        return request.user.is_authenticated and request.user.user_type == "coach"


class IsPlayer(permissions.BasePermission):
    """Permission for players."""

    def has_permission(self, request, view):
        """
        Check if user is a player.

        Returns:
            bool: True if user is authenticated and a player
        """
        return request.user.is_authenticated and request.user.user_type == "player"


class IsParent(permissions.BasePermission):
    """Permission for parents."""

    def has_permission(self, request, view):
        """
        Check if user is a parent.

        Returns:
            bool: True if user is authenticated and a parent
        """
        return request.user.is_authenticated and request.user.user_type == "parent"


class IsAcademyMember(permissions.BasePermission):
    """Permission for academy members (admin, coach, player, parent)."""

    def has_permission(self, request, view):
        """
        Check if user is a member of an academy.

        Returns:
            bool: True if user is authenticated and has an academy role
        """
        return request.user.is_authenticated and request.user.user_type in [
            "academy_admin",
            "coach",
            "player",
            "parent",
        ]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission for object owners or read-only access."""

    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the object or request is read-only.

        Returns:
            bool: True if request is safe or user owns object
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
