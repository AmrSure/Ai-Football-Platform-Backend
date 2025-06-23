"""Bookings views module for the AI Football Platform.

This module contains views for managing fields, bookings, and booking-related
operations with atomic transaction support.
"""

import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAcademyAdmin, IsSystemAdmin
from apps.core.views import AcademyScopedViewSet, BaseModelViewSet

from .models import Field, FieldBooking
from .serializers import FieldBookingSerializer, FieldSerializer

logger = logging.getLogger(__name__)


class FieldViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing sports fields with atomic transaction support.

    list: Returns a paginated list of fields
    retrieve: Returns details of a specific field
    create: Creates a new field (academy admin only)
    update: Updates field data (academy admin only)
    partial_update: Partially updates field data (academy admin only)
    destroy: Deletes a field (academy admin only)
    availability: Check field availability for a given time period

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "field_type", "academy__name"]
    filterset_fields = ["field_type", "is_available", "is_active", "academy"]
    ordering = ["name"]

    def get_permissions(self):
        """
        Academy admins can manage fields in their academy.
        System admins can manage all fields.
        Other users can only view fields.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List fields",
        operation_description="Returns a paginated list of fields based on user permissions",
        responses={
            200: "List of fields",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve field details",
        operation_description="Returns details of a specific field",
        responses={
            200: "Field details",
            401: "Unauthorized - authentication required",
            404: "Not found - field does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new field",
        operation_description="Creates a new field (academy admin only)",
        responses={
            201: "Field created successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update field",
        operation_description="Updates field data (academy admin only)",
        responses={
            200: "Field updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this field",
            404: "Not found - field does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update field",
        operation_description="Partially updates field data (academy admin only)",
        responses={
            200: "Field updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this field",
            404: "Not found - field does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete field",
        operation_description="Deletes a field (academy admin only)",
        responses={
            204: "No content - field deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this field",
            404: "Not found - field does not exist",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Check field availability",
        operation_description="Check if a field is available for a given time period",
        manual_parameters=[
            openapi.Parameter(
                "start_time",
                openapi.IN_QUERY,
                description="Start time (ISO format: YYYY-MM-DDTHH:MM:SS)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "end_time",
                openapi.IN_QUERY,
                description="End time (ISO format: YYYY-MM-DDTHH:MM:SS)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Availability status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "available": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "conflicting_bookings": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            ),
            400: "Bad request - invalid time format or missing parameters",
            401: "Unauthorized - authentication required",
            404: "Not found - field does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """
        Check field availability for a given time period.
        """
        field = self.get_object()
        start_time_str = request.query_params.get("start_time")
        end_time_str = request.query_params.get("end_time")

        if not start_time_str or not end_time_str:
            return Response(
                {"error": "start_time and end_time parameters are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        except ValueError:
            return Response(
                {
                    "error": "Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_time >= end_time:
            return Response(
                {"error": "start_time must be before end_time"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for conflicting bookings
        conflicting_bookings = FieldBooking.objects.filter(
            field=field,
            status__in=["pending", "confirmed"],
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        available = not conflicting_bookings.exists() and field.is_available

        response_data = {
            "available": available,
            "conflicting_bookings": [
                {
                    "id": booking.id,
                    "start_time": booking.start_time,
                    "end_time": booking.end_time,
                    "status": booking.status,
                    "booked_by": booking.booked_by.email,
                }
                for booking in conflicting_bookings
            ],
        }

        logger.info(
            f"Checked availability for field {field.id} from {start_time} to {end_time}: {available}"
        )
        return Response(response_data)


class FieldBookingViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing field bookings with atomic transaction support.

    list: Returns a paginated list of bookings
    retrieve: Returns details of a specific booking
    create: Creates a new booking
    update: Updates booking data
    partial_update: Partially updates booking data
    destroy: Deletes a booking
    confirm: Confirms a pending booking
    cancel: Cancels a booking
    complete: Marks a booking as completed

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = FieldBooking.objects.all()
    serializer_class = FieldBookingSerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "field__name",
        "booked_by__email",
        "booked_by__first_name",
        "booked_by__last_name",
    ]
    filterset_fields = ["field", "status", "field__academy", "booked_by"]
    ordering = ["-start_time"]

    def get_queryset(self):
        """
        Return bookings based on user permissions and academy scope.
        """
        queryset = super().get_queryset()
        user = self.request.user

        # Filter based on user permissions
        if user.user_type == "external_client":
            # External clients can only see their own bookings
            return queryset.filter(booked_by=user)
        elif user.user_type in ["coach", "player", "parent"] and hasattr(
            user, "profile"
        ):
            # Academy users can see bookings for their academy's fields
            if hasattr(user.profile, "academy"):
                return queryset.filter(field__academy=user.profile.academy)
        elif user.user_type == "academy_admin" and hasattr(user, "profile"):
            # Academy admins can see all bookings for their academy's fields
            if hasattr(user.profile, "academy"):
                return queryset.filter(field__academy=user.profile.academy)
        elif user.user_type == "system_admin":
            # System admins can see all bookings
            return queryset

        return queryset.none()

    @swagger_auto_schema(
        operation_summary="List bookings",
        operation_description="Returns a paginated list of bookings based on user permissions",
        responses={
            200: "List of bookings",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve booking details",
        operation_description="Returns details of a specific booking",
        responses={
            200: "Booking details",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this booking",
            404: "Not found - booking does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new booking",
        operation_description="Creates a new field booking",
        responses={
            201: "Booking created successfully",
            400: "Bad request - validation errors or field not available",
            401: "Unauthorized - authentication required",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create booking with atomic transaction and availability check.
        """
        field = serializer.validated_data["field"]
        start_time = serializer.validated_data["start_time"]
        end_time = serializer.validated_data["end_time"]

        # Check for conflicting bookings
        conflicting_bookings = FieldBooking.objects.filter(
            field=field,
            status__in=["pending", "confirmed"],
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if conflicting_bookings.exists():
            logger.warning(
                f"Booking conflict detected for field {field.id} from {start_time} to {end_time}"
            )
            raise serializers.ValidationError(
                "Field is not available for the selected time period"
            )

        if not field.is_available:
            logger.warning(f"Attempted to book unavailable field {field.id}")
            raise serializers.ValidationError(
                "Field is currently not available for booking"
            )

        booking = serializer.save(booked_by=self.request.user)
        logger.info(
            f"Created booking {booking.id} for field {field.id} by user {self.request.user.id}"
        )

    @swagger_auto_schema(
        operation_summary="Confirm booking",
        operation_description="Confirms a pending booking (academy admin only)",
        responses={
            200: openapi.Response(
                description="Booking confirmed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Updated status"
                        ),
                    },
                ),
            ),
            400: "Bad request - booking cannot be confirmed",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - booking does not exist",
        },
    )
    @transaction.atomic
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAcademyAdmin],
    )
    def confirm(self, request, pk=None):
        """
        Confirm a pending booking.
        """
        try:
            booking = self.get_object()

            if booking.status != "pending":
                return Response(
                    {"error": f"Cannot confirm booking with status '{booking.status}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            booking.status = "confirmed"
            booking.save()
            logger.info(f"Confirmed booking {booking.id} by admin {request.user.id}")
            return Response({"status": "confirmed"})
        except Exception as e:
            logger.error(f"Error confirming booking {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Cancel booking",
        operation_description="Cancels a booking",
        responses={
            200: openapi.Response(
                description="Booking cancelled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Updated status"
                        ),
                    },
                ),
            ),
            400: "Bad request - booking cannot be cancelled",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this booking",
            404: "Not found - booking does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        """
        try:
            booking = self.get_object()

            if booking.status in ["cancelled", "completed"]:
                return Response(
                    {"error": f"Cannot cancel booking with status '{booking.status}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            booking.status = "cancelled"
            booking.save()
            logger.info(f"Cancelled booking {booking.id} by user {request.user.id}")
            return Response({"status": "cancelled"})
        except Exception as e:
            logger.error(f"Error cancelling booking {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Complete booking",
        operation_description="Marks a booking as completed (academy admin only)",
        responses={
            200: openapi.Response(
                description="Booking completed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Updated status"
                        ),
                    },
                ),
            ),
            400: "Bad request - booking cannot be completed",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - booking does not exist",
        },
    )
    @transaction.atomic
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAcademyAdmin],
    )
    def complete(self, request, pk=None):
        """
        Mark a booking as completed.
        """
        try:
            booking = self.get_object()

            if booking.status != "confirmed":
                return Response(
                    {
                        "error": f"Cannot complete booking with status '{booking.status}'"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            booking.status = "completed"
            booking.save()
            logger.info(f"Completed booking {booking.id} by admin {request.user.id}")
            return Response({"status": "completed"})
        except Exception as e:
            logger.error(f"Error completing booking {pk}: {str(e)}")
            raise
