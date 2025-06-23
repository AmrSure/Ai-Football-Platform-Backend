"""Core views module for the AI Football Platform.

This module contains base viewsets and view mixins used across the application.
It provides consistent API behavior and utility functions for REST endpoints.
"""

import logging

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base viewset with common functionality for all model viewsets.

    Provides filtering, searching, ordering, and active status handling with
    atomic transaction support for all database operations.

    Features:
    - Filters out inactive objects by default
    - Automatically sets created_by to current user if model supports it
    - Provides toggle_active action to enable/disable objects
    - Includes common filter backends
    - Atomic transactions for all write operations
    - Proper error logging and handling

    Dependencies:
    - Django REST Framework's ModelViewSet
    - DjangoFilterBackend, SearchFilter, OrderingFilter for query filtering
    - Django's transaction module for atomic operations
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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new object with atomic transaction.

        Ensures that all database operations during object creation
        are executed atomically to maintain data consistency.
        """
        try:
            logger.info(
                f"Creating new {self.get_serializer().Meta.model.__name__} by user {request.user.id}"
            )
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error creating {self.get_serializer().Meta.model.__name__}: {str(e)}"
            )
            raise

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update an object with atomic transaction.

        Ensures that all database operations during object update
        are executed atomically to maintain data consistency.
        """
        try:
            obj = self.get_object()
            logger.info(
                f"Updating {obj.__class__.__name__} {obj.pk} by user {request.user.id}"
            )
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating object: {str(e)}")
            raise

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an object with atomic transaction.

        Ensures that all database operations during object partial update
        are executed atomically to maintain data consistency.
        """
        try:
            obj = self.get_object()
            logger.info(
                f"Partially updating {obj.__class__.__name__} {obj.pk} by user {request.user.id}"
            )
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error partially updating object: {str(e)}")
            raise

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Delete an object with atomic transaction.

        Ensures that all database operations during object deletion
        are executed atomically to maintain data consistency.
        """
        try:
            obj = self.get_object()
            logger.info(
                f"Deleting {obj.__class__.__name__} {obj.pk} by user {request.user.id}"
            )
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting object: {str(e)}")
            raise

    def perform_create(self, serializer):
        """
        Override to automatically set created_by field to current user.

        Only sets the field if the model has a created_by field.
        Executed within the atomic transaction of the create method.
        """
        if hasattr(serializer.Meta.model, "created_by"):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle active status of object with atomic transaction.

        Provides an endpoint to enable/disable objects without deleting them.
        All operations are executed atomically to ensure consistency.
        """
        try:
            obj = self.get_object()
            if hasattr(obj, "is_active"):
                old_status = obj.is_active
                obj.is_active = not obj.is_active
                obj.save()
                status_value = "active" if obj.is_active else "inactive"
                logger.info(
                    f"Toggled {obj.__class__.__name__} {obj.pk} from {old_status} to {obj.is_active}"
                )
                return Response({"status": status_value})
            return Response(
                {"error": "Object does not support active status"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error toggling active status: {str(e)}")
            raise


class AcademyScopedViewSet(BaseModelViewSet):
    """
    Base viewset for academy-scoped resources with atomic transaction support.

    Filters queryset based on user's academy access permissions and ensures
    all database operations are executed atomically.

    Features:
    - System admins see all resources
    - Academy users only see resources from their academy
    - Other users see no resources
    - Atomic transactions for all write operations
    - Proper error logging and handling

    Dependencies:
    - BaseModelViewSet as parent class
    - User model with user_type and profile relationship
    - Django's transaction module for atomic operations
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
