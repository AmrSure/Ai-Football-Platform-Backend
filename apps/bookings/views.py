"""Bookings views module for the AI Football Platform.

This module contains views for managing fields, bookings, and booking-related
operations with atomic transaction support and email notifications.
"""

import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAcademyAdmin, IsSystemAdmin
from apps.core.views import AcademyScopedViewSet, BaseModelViewSet

from .models import Field, FieldBooking
from .serializers import (
    BookingAvailabilitySerializer,
    BookingStatisticsSerializer,
    FieldBookingSerializer,
    FieldSerializer,
)
from .utils import (
    BookingConflictChecker,
    BookingEmailService,
    BookingStatisticsCalculator,
)

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

    def get_queryset(self):
        """
        Override to handle external client access to all fields.
        External clients should see all available fields across all academies.
        """
        queryset = super().get_queryset()
        user = self.request.user

        # External clients can see all fields
        if user.user_type == "external_client":
            return Field.objects.all()

        # For other users, use the default AcademyScopedViewSet behavior
        return queryset

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

    @swagger_auto_schema(
        operation_summary="Get field utilization statistics",
        operation_description="Get comprehensive utilization statistics for a specific field",
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start date for statistics (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End date for statistics (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "period",
                openapi.IN_QUERY,
                description="Time period for grouping (daily, weekly, monthly, yearly)",
                type=openapi.TYPE_STRING,
                required=False,
                default="monthly",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Field utilization statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "field_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "field_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "period": openapi.Schema(type=openapi.TYPE_STRING),
                        "date_range": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "start_date": openapi.Schema(type=openapi.TYPE_STRING),
                                "end_date": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "utilization_stats": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "total_hours_available": openapi.Schema(
                                    type=openapi.TYPE_NUMBER
                                ),
                                "total_hours_booked": openapi.Schema(
                                    type=openapi.TYPE_NUMBER
                                ),
                                "total_bookings": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "utilization_rate": openapi.Schema(
                                    type=openapi.TYPE_NUMBER
                                ),
                                "average_booking_duration": openapi.Schema(
                                    type=openapi.TYPE_NUMBER
                                ),
                                "peak_hours": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING),
                                ),
                                "least_busy_hours": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING),
                                ),
                            },
                        ),
                        "revenue_stats": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "total_revenue": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "average_revenue_per_booking": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "average_revenue_per_hour": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "projected_monthly_revenue": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                            },
                        ),
                        "booking_trends": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                        "user_type_breakdown": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - field does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def utilization(self, request, pk=None):
        """
        Get field utilization statistics.
        """
        field = self.get_object()

        # Get date range and period from query params
        from decimal import Decimal

        from django.utils.dateparse import parse_date

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        period = request.query_params.get("period", "monthly")

        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Get basic utilization stats
        basic_stats = BookingStatisticsCalculator.get_field_utilization_rate(
            field=field, start_date=start_date, end_date=end_date
        )

        # Get booking queryset for detailed stats
        queryset = field.bookings.filter(status__in=["confirmed", "completed"])
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)

        # Calculate revenue stats
        revenue_aggregates = queryset.aggregate(
            total_revenue=Sum("total_cost"),
            average_revenue_per_booking=Avg("total_cost"),
        )

        total_revenue = float(revenue_aggregates["total_revenue"] or 0)
        avg_revenue_per_booking = float(
            revenue_aggregates["average_revenue_per_booking"] or 0
        )
        avg_revenue_per_hour = float(field.hourly_rate)

        # Calculate booking trends based on period
        booking_trends = []
        if period == "weekly" and start_date and end_date:
            current_date = start_date
            week_num = 1
            while current_date <= end_date:
                week_end = min(current_date + timedelta(days=6), end_date)
                week_queryset = queryset.filter(
                    start_time__date__gte=current_date, start_time__date__lte=week_end
                )
                week_bookings = week_queryset.aggregate(
                    count=Count("id"), revenue=Sum("total_cost")
                )

                # Calculate total hours manually since duration_hours is a property
                total_hours = sum(booking.duration_hours for booking in week_queryset)

                total_hours = float(total_hours)
                week_available_hours = 7 * 14  # 7 days * 14 hours per day
                week_utilization = (
                    (total_hours / week_available_hours * 100)
                    if week_available_hours > 0
                    else 0
                )

                booking_trends.append(
                    {
                        "week": week_num,
                        "week_start": current_date.strftime("%Y-%m-%d"),
                        "bookings": week_bookings["count"] or 0,
                        "revenue": str(week_bookings["revenue"] or 0),
                        "utilization": round(week_utilization, 1),
                    }
                )

                current_date = week_end + timedelta(days=1)
                week_num += 1

        # Calculate peak hours
        peak_hours = []
        least_busy_hours = []
        hour_bookings = {}

        if queryset.exists():
            # Group bookings by hour to find peak times
            for booking in queryset:
                hour = booking.start_time.hour
                hour_key = f"{hour:02d}:00-{(hour + 1):02d}:00"
                if hour_key not in hour_bookings:
                    hour_bookings[hour_key] = 0
                hour_bookings[hour_key] += 1

            # Sort by booking count and get top hours
            sorted_hours = sorted(
                hour_bookings.items(), key=lambda x: x[1], reverse=True
            )
            peak_hours = [hour for hour, count in sorted_hours[:2]]

            # Calculate least busy hours (opposite of peak hours)
            least_busy_sorted = sorted(hour_bookings.items(), key=lambda x: x[1])
            least_busy_hours = [hour for hour, count in least_busy_sorted[:2]]

        # Calculate projected revenue (if we have current data)
        projected_revenue = total_revenue
        if period == "monthly" and queryset.exists():
            if start_date and end_date:
                days_in_period = (end_date - start_date).days + 1
                if days_in_period < 30:
                    # Project to full month
                    projected_revenue = total_revenue * (30 / days_in_period)

        response_data = {
            "field_id": field.id,
            "field_name": field.name,
            "period": period,
            "date_range": {
                "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
                "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
            },
            "utilization_stats": {
                "total_hours_available": basic_stats["total_available_hours"],
                "total_hours_booked": basic_stats["total_booked_hours"],
                "total_bookings": basic_stats["booking_count"],
                "utilization_rate": basic_stats["utilization_rate"],
                "average_booking_duration": round(
                    basic_stats["total_booked_hours"] / basic_stats["booking_count"], 1
                )
                if basic_stats["booking_count"] > 0
                else 0,
                "peak_hours": peak_hours,
                "least_busy_hours": least_busy_hours,
            },
            "revenue_stats": {
                "total_revenue": f"{total_revenue:.2f}",
                "average_revenue_per_booking": f"{avg_revenue_per_booking:.2f}",
                "average_revenue_per_hour": f"{avg_revenue_per_hour:.2f}",
                "projected_monthly_revenue": f"{projected_revenue:.2f}",
            },
        }

        # Add booking trends if available
        if booking_trends:
            response_data["booking_trends"] = booking_trends

        # Add user type breakdown
        user_type_breakdown = {
            "internal_bookings": {
                "total": queryset.filter(
                    booked_by__user_type__in=["coach", "player", "parent"]
                ).count(),
                "revenue": str(
                    queryset.filter(
                        booked_by__user_type__in=["coach", "player", "parent"]
                    ).aggregate(revenue=Sum("total_cost"))["revenue"]
                    or 0
                ),
            },
            "external_bookings": {
                "total": queryset.filter(
                    booked_by__user_type="external_client"
                ).count(),
                "revenue": str(
                    queryset.filter(booked_by__user_type="external_client").aggregate(
                        revenue=Sum("total_cost")
                    )["revenue"]
                    or 0
                ),
            },
        }
        response_data["user_type_breakdown"] = user_type_breakdown

        return Response(response_data)

    @swagger_auto_schema(
        operation_summary="Get field schedule",
        operation_description="Get booking schedule for a specific field",
        manual_parameters=[
            openapi.Parameter(
                "date",
                openapi.IN_QUERY,
                description="Date for schedule (YYYY-MM-DD, defaults to today)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "days",
                openapi.IN_QUERY,
                description="Number of days to show (default: 7)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Field schedule",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - field does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def schedule(self, request, pk=None):
        """
        Get field booking schedule.
        """
        field = self.get_object()

        # Get date range from query params
        from datetime import date

        from django.utils.dateparse import parse_date

        start_date = request.query_params.get("date")
        days = int(request.query_params.get("days", 7))

        if start_date:
            start_date = parse_date(start_date)
        else:
            start_date = date.today()

        end_date = start_date + timedelta(days=days)

        # Get bookings for the date range
        bookings = field.bookings.filter(
            start_time__date__gte=start_date,
            start_time__date__lt=end_date,
            status__in=["confirmed", "pending"],
        ).order_by("start_time")

        # Group bookings by date
        schedule = {}
        for booking in bookings:
            booking_date = booking.start_time.date()
            if booking_date not in schedule:
                schedule[booking_date] = []

            schedule[booking_date].append(
                {
                    "id": booking.id,
                    "start_time": booking.start_time,
                    "end_time": booking.end_time,
                    "status": booking.status,
                    "booked_by": booking.booked_by.get_full_name()
                    or booking.booked_by.email,
                    "total_cost": booking.total_cost,
                    "notes": booking.notes,
                }
            )

        # Create daily schedule including empty days
        daily_schedule = []
        current_date = start_date
        while current_date < end_date:
            daily_schedule.append(
                {"date": current_date, "bookings": schedule.get(current_date, [])}
            )
            current_date += timedelta(days=1)

        return Response(daily_schedule)


class FieldBookingViewSet(BaseModelViewSet):
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
        Create booking with atomic transaction, availability check, and email notifications.
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

        booking = serializer.save()
        logger.info(
            f"Created booking {booking.id} for field {field.id} by user {self.request.user.id} for user {booking.booked_by.id}"
        )

        # Send email notifications
        try:
            # Send confirmation email to customer
            BookingEmailService.send_booking_created_email(booking)

            # Notify academy admin of new booking
            BookingEmailService.notify_academy_admin_new_booking(booking)

            logger.info(f"Email notifications sent for booking {booking.id}")
        except Exception as email_error:
            logger.error(
                f"Failed to send email notifications for booking {booking.id}: {str(email_error)}"
            )
            # Don't raise exception for email failures, booking should still succeed

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

            # Send confirmation email to customer
            try:
                BookingEmailService.send_booking_confirmed_email(booking)
                logger.info(f"Booking confirmation email sent for booking {booking.id}")
            except Exception as email_error:
                logger.error(
                    f"Failed to send confirmation email for booking {booking.id}: {str(email_error)}"
                )

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

            # Check if cancellation is by admin or customer
            is_admin_cancellation = (
                hasattr(request.user, "academy_admin_profile")
                and request.user.academy_admin_profile
                and request.user.academy_admin_profile.academy == booking.field.academy
            )

            booking.status = "cancelled"
            booking.save()

            # Send cancellation email to customer
            try:
                BookingEmailService.send_booking_cancelled_email(
                    booking, cancelled_by_admin=is_admin_cancellation
                )
                logger.info(f"Booking cancellation email sent for booking {booking.id}")
            except Exception as email_error:
                logger.error(
                    f"Failed to send cancellation email for booking {booking.id}: {str(email_error)}"
                )

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

            # Send completion email to customer
            try:
                BookingEmailService.send_booking_completed_email(booking)
                logger.info(f"Booking completion email sent for booking {booking.id}")
            except Exception as email_error:
                logger.error(
                    f"Failed to send completion email for booking {booking.id}: {str(email_error)}"
                )

            logger.info(f"Completed booking {booking.id} by admin {request.user.id}")
            return Response({"status": "completed"})
        except Exception as e:
            logger.error(f"Error completing booking {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Check booking availability",
        operation_description="Check if a field is available for a specific time period",
        request_body=BookingAvailabilitySerializer,
        responses={
            200: openapi.Response(
                description="Availability check result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "available": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "conflicts": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                        "suggestions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                        "reason": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
        },
    )
    @action(detail=False, methods=["post"])
    def check_availability(self, request):
        """
        Check field availability for a given time period with alternative suggestions.
        """
        serializer = BookingAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            field = Field.objects.get(id=serializer.validated_data["field_id"])
        except Field.DoesNotExist:
            return Response(
                {"error": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )

        availability = BookingConflictChecker.check_field_availability(
            field=field,
            start_time=serializer.validated_data["start_time"],
            end_time=serializer.validated_data["end_time"],
        )

        # Serialize conflict data
        conflicts_data = []
        for conflict in availability.get("conflicts", []):
            conflicts_data.append(
                {
                    "id": conflict.id,
                    "start_time": conflict.start_time,
                    "end_time": conflict.end_time,
                    "status": conflict.status,
                    "booked_by": conflict.booked_by.email,
                }
            )

        availability["conflicts"] = conflicts_data
        return Response(availability)

    @swagger_auto_schema(
        operation_summary="Get my bookings",
        operation_description="Get all bookings made by the current user",
        responses={
            200: "List of user's bookings",
            401: "Unauthorized - authentication required",
        },
    )
    @action(detail=False, methods=["get"])
    def my_bookings(self, request):
        """
        Get all bookings for the current user.
        """
        queryset = self.get_queryset().filter(booked_by=request.user)

        # Apply filtering
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get academy booking statistics",
        operation_description="Get booking statistics for academy admin",
        responses={
            200: BookingStatisticsSerializer,
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsAcademyAdmin],
    )
    def statistics(self, request):
        """
        Get booking statistics for the academy.
        """
        # Get academy from user
        try:
            academy = request.user.academy_admin_profile.academy
        except Exception:
            return Response(
                {"error": "User is not associated with any academy"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get date range from query params
        from django.utils.dateparse import parse_date

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        stats = BookingStatisticsCalculator.get_academy_booking_stats(
            academy_id=academy.id, start_date=start_date, end_date=end_date
        )

        return Response(stats)

    @swagger_auto_schema(
        operation_summary="Send booking reminder",
        operation_description="Send reminder email for upcoming booking",
        responses={
            200: "Reminder sent successfully",
            400: "Bad request - booking not eligible for reminder",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this booking",
            404: "Not found - booking does not exist",
        },
    )
    @action(detail=True, methods=["post"])
    def send_reminder(self, request, pk=None):
        """
        Send booking reminder email.
        """
        booking = self.get_object()

        # Check if booking is confirmed and in the future
        if booking.status != "confirmed":
            return Response(
                {"error": "Can only send reminders for confirmed bookings"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.start_time <= timezone.now():
            return Response(
                {"error": "Cannot send reminder for past bookings"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            BookingEmailService.send_booking_reminder_email(booking)
            logger.info(f"Reminder email sent for booking {booking.id}")
            return Response({"message": "Reminder sent successfully"})
        except Exception as e:
            logger.error(f"Failed to send reminder for booking {booking.id}: {str(e)}")
            return Response(
                {"error": "Failed to send reminder email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
