"""Core views module for the AI Football Platform.

This module contains base viewsets and view mixins used across the application.
It provides consistent API behavior and utility functions for REST endpoints.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base viewset with common functionality for all model viewsets.

    Provides filtering, searching, ordering, and active status handling.

    Features:
    - Filters out inactive objects by default
    - Automatically sets created_by to current user if model supports it
    - Provides toggle_active action to enable/disable objects
    - Includes common filter backends

    Dependencies:
    - Django REST Framework's ModelViewSet
    - DjangoFilterBackend, SearchFilter, OrderingFilter for query filtering
    """

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Default ordering will be set in get_queryset based on available fields

    def get_queryset(self):
        """
        Override to filter out inactive objects by default.

        Only returns objects where is_active=True if the model has that field.
        Also sets appropriate ordering based on available date fields.
        """
        queryset = super().get_queryset()

        # Apply default ordering based on available fields
        model = queryset.model
        if not self.ordering:
            if hasattr(model, "created_at"):
                queryset = queryset.order_by("-created_at")
            elif hasattr(model, "date_joined"):
                queryset = queryset.order_by("-date_joined")
            elif hasattr(model, "date_created"):
                queryset = queryset.order_by("-date_created")
            elif hasattr(model, "updated_at"):
                queryset = queryset.order_by("-updated_at")

        # Filter by active status if applicable
        if hasattr(model, "is_active"):
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        """
        Override to automatically set created_by field to current user.

        Only sets the field if the model has a created_by field.
        """
        if hasattr(serializer.Meta.model, "created_by"):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle active status of object.

        Provides an endpoint to enable/disable objects without deleting them.
        """
        obj = self.get_object()
        if hasattr(obj, "is_active"):
            obj.is_active = not obj.is_active
            obj.save()
            status_value = "active" if obj.is_active else "inactive"
            return Response({"status": status_value})
        return Response(
            {"error": "Object does not support active status"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AcademyScopedViewSet(BaseModelViewSet):
    """
    Base viewset for academy-scoped resources.

    Filters queryset based on user's academy access permissions.

    Features:
    - System admins see all resources
    - Academy users only see resources from their academy
    - Other users see no resources

    Dependencies:
    - BaseModelViewSet as parent class
    - User model with user_type and profile relationship
    """

    def get_queryset(self):
        """
        Override to filter queryset based on user's academy access.

        Implements academy-level access control.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == "system_admin":
            return queryset
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            return queryset.filter(academy=user.profile.academy)
        return queryset.none()
