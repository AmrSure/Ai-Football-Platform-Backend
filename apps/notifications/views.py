"""Notifications views module for the AI Football Platform.

This module contains views for managing notifications and notification preferences
with atomic transaction support.
"""

import logging

from django.db import models, transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.views import BaseModelViewSet

from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)


class NotificationViewSet(BaseModelViewSet):
    """
    API endpoints for managing notifications with atomic transaction support.

    list: Returns a paginated list of user's notifications
    retrieve: Returns details of a specific notification
    mark_as_read: Mark a notification as read
    mark_all_as_read: Mark all notifications as read
    unread_count: Get count of unread notifications

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["title", "message", "notification_type"]
    filterset_fields = ["notification_type", "is_read", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Return only notifications for the current user.
        """
        if not self.request.user.is_authenticated:
            return Notification.objects.none()

        return Notification.objects.filter(recipient=self.request.user, is_active=True)

    @swagger_auto_schema(
        operation_summary="List user notifications",
        operation_description="Returns a paginated list of notifications for the authenticated user",
        responses={
            200: "List of notifications",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve notification details",
        operation_description="Returns details of a specific notification",
        responses={
            200: "Notification details",
            401: "Unauthorized - authentication required",
            404: "Not found - notification does not exist or does not belong to user",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        """
        All actions require authentication.
        Users can only access their own notifications.
        """
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="Mark notification as read",
        operation_description="Marks a specific notification as read",
        responses={
            200: openapi.Response(
                description="Notification marked as read",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - notification does not exist or does not belong to user",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        try:
            notification = self.get_object()

            if notification.is_read:
                return Response(
                    {"status": "Notification was already read"},
                    status=status.HTTP_200_OK,
                )

            notification.is_read = True
            notification.save()
            logger.info(
                f"Marked notification {notification.id} as read for user {request.user.id}"
            )
            return Response({"status": "Notification marked as read"})
        except Exception as e:
            logger.error(f"Error marking notification {pk} as read: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Mark all notifications as read",
        operation_description="Marks all unread notifications as read for the authenticated user",
        responses={
            200: openapi.Response(
                description="All notifications marked as read",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "marked_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Number of notifications marked",
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
        },
    )
    @transaction.atomic
    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """
        Mark all unread notifications as read for the authenticated user.
        """
        try:
            unread_notifications = self.get_queryset().filter(is_read=False)
            marked_count = unread_notifications.update(is_read=True)

            logger.info(
                f"Marked {marked_count} notifications as read for user {request.user.id}"
            )
            return Response(
                {
                    "status": "All notifications marked as read",
                    "marked_count": marked_count,
                }
            )
        except Exception as e:
            logger.error(
                f"Error marking all notifications as read for user {request.user.id}: {str(e)}"
            )
            raise

    @swagger_auto_schema(
        operation_summary="Get unread notification count",
        operation_description="Returns the count of unread notifications for the authenticated user",
        responses={
            200: openapi.Response(
                description="Unread notification count",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "unread_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Number of unread notifications",
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
        },
    )
    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Get count of unread notifications for the authenticated user.
        """
        unread_count = self.get_queryset().filter(is_read=False).count()
        logger.info(f"User {request.user.id} has {unread_count} unread notifications")
        return Response({"unread_count": unread_count})

    @swagger_auto_schema(
        operation_summary="Delete notification",
        operation_description="Deletes a notification (soft delete)",
        responses={
            204: "No content - notification deleted successfully",
            401: "Unauthorized - authentication required",
            404: "Not found - notification does not exist or does not belong to user",
        },
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a notification by setting is_active to False.
        """
        try:
            notification = self.get_object()
            notification.is_active = False
            notification.save()
            logger.info(
                f"Soft deleted notification {notification.id} for user {request.user.id}"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Get notification statistics",
        operation_description="Returns notification statistics for the authenticated user",
        responses={
            200: openapi.Response(
                description="Notification statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_notifications": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        "unread_notifications": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        "read_notifications": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "notifications_by_type": openapi.Schema(
                            type=openapi.TYPE_OBJECT
                        ),
                        "notifications_by_priority": openapi.Schema(
                            type=openapi.TYPE_OBJECT
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
        },
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        Get notification statistics for the authenticated user.
        """
        queryset = self.get_queryset()

        total_notifications = queryset.count()
        unread_notifications = queryset.filter(is_read=False).count()
        read_notifications = total_notifications - unread_notifications

        # Notifications by type
        type_stats = (
            queryset.values("notification_type")
            .annotate(count=models.Count("notification_type"))
            .order_by("-count")
        )
        notifications_by_type = {
            stat["notification_type"]: stat["count"] for stat in type_stats
        }

        # Notifications by priority
        priority_stats = (
            queryset.values("priority")
            .annotate(count=models.Count("priority"))
            .order_by("-count")
        )
        notifications_by_priority = {
            stat["priority"]: stat["count"] for stat in priority_stats
        }

        stats = {
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "read_notifications": read_notifications,
            "notifications_by_type": notifications_by_type,
            "notifications_by_priority": notifications_by_priority,
        }

        logger.info(f"Generated notification statistics for user {request.user.id}")
        return Response(stats)
