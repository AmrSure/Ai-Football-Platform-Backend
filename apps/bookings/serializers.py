"""Serializers for the bookings app.

This module contains serializers for Field and FieldBooking models with
comprehensive validation and conflict detection.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from apps.academies.serializers import AcademySerializer
from apps.core.serializers import BaseUserSerializer

from .models import Field, FieldBooking


class FieldSerializer(serializers.ModelSerializer):
    """
    Serializer for Field model with nested academy information.
    """

    academy_name = serializers.CharField(source="academy.name", read_only=True)
    academy_details = AcademySerializer(source="academy", read_only=True)
    booking_count = serializers.SerializerMethodField()
    next_available_slot = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = [
            "id",
            "academy",
            "academy_name",
            "academy_details",
            "name",
            "field_type",
            "capacity",
            "hourly_rate",
            "facilities",
            "is_available",
            "is_active",
            "booking_count",
            "next_available_slot",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "academy_name",
            "academy_details",
            "booking_count",
            "next_available_slot",
        ]

    def get_booking_count(self, obj):
        """Get the total number of confirmed bookings for this field."""
        return obj.bookings.filter(status="confirmed").count()

    def get_next_available_slot(self, obj):
        """Get the next available time slot for this field."""
        now = timezone.now()
        next_booking = (
            obj.bookings.filter(start_time__gt=now, status__in=["confirmed", "pending"])
            .order_by("start_time")
            .first()
        )

        if next_booking:
            return {
                "available_from": now.isoformat(),
                "available_until": next_booking.start_time.isoformat(),
                "next_booking_start": next_booking.start_time.isoformat(),
            }
        return {
            "available_from": now.isoformat(),
            "available_until": None,
            "next_booking_start": None,
        }


class FieldBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for FieldBooking model with comprehensive validation and
    conflict detection.
    """

    field_name = serializers.CharField(source="field.name", read_only=True)
    field_details = FieldSerializer(source="field", read_only=True)
    booked_by_name = serializers.CharField(
        source="booked_by.get_full_name", read_only=True
    )
    booked_by_email = serializers.CharField(source="booked_by.email", read_only=True)
    booked_by_details = BaseUserSerializer(source="booked_by", read_only=True)
    academy_name = serializers.CharField(source="field.academy.name", read_only=True)
    duration_hours = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    can_modify = serializers.SerializerMethodField()

    class Meta:
        model = FieldBooking
        fields = [
            "id",
            "field",
            "field_name",
            "field_details",
            "booked_by",
            "booked_by_name",
            "booked_by_email",
            "booked_by_details",
            "academy_name",
            "start_time",
            "end_time",
            "duration_hours",
            "total_cost",
            "status",
            "notes",
            "match",
            "can_cancel",
            "can_modify",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "field_name",
            "field_details",
            "booked_by_name",
            "booked_by_email",
            "booked_by_details",
            "academy_name",
            "duration_hours",
            "can_cancel",
            "can_modify",
        ]

    def get_fields(self):
        """
        Make booked_by field writable for academy admins and system admins.
        """
        fields = super().get_fields()

        # Check if user is academy admin or system admin
        request = self.context.get("request")
        if request and request.user:
            user = request.user
            if user.user_type in ["academy_admin", "system_admin"]:
                # Remove booked_by from read_only_fields for admins
                if "booked_by" in fields:
                    fields["booked_by"].read_only = False
                    fields["booked_by"].required = False  # Make it optional
            else:
                # For regular users, keep booked_by as read-only
                if "booked_by" in fields:
                    fields["booked_by"].read_only = True

        return fields

    def get_duration_hours(self, obj):
        """Calculate booking duration in hours."""
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return round(duration.total_seconds() / 3600, 2)
        return 0

    def get_can_cancel(self, obj):
        """Check if booking can be cancelled."""
        if obj.status in ["cancelled", "completed"]:
            return False
        # Can cancel up to 2 hours before start time
        now = timezone.now()
        if obj.start_time <= now + timedelta(hours=2):
            return False
        return True

    def get_can_modify(self, obj):
        """Check if booking can be modified."""
        if obj.status in ["cancelled", "completed"]:
            return False
        # Can modify up to 4 hours before start time
        now = timezone.now()
        if obj.start_time <= now + timedelta(hours=4):
            return False
        return True

    def validate(self, data):
        """
        Validate booking data including conflict detection and business rules.
        """
        field = data.get("field")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        booked_by = data.get("booked_by")

        # Validate booked_by field for admins
        request = self.context.get("request")
        if request and request.user:
            user = request.user
            if user.user_type in ["academy_admin", "system_admin"]:
                # If booked_by is provided, validate it
                if booked_by:
                    # For academy admins, ensure the user belongs to their academy
                    if user.user_type == "academy_admin":
                        if hasattr(user, "profile") and hasattr(
                            user.profile, "academy"
                        ):
                            user_academy = user.profile.academy
                            # Check if the booked_by user belongs to the same academy
                            if hasattr(booked_by, "profile") and hasattr(
                                booked_by.profile, "academy"
                            ):
                                if booked_by.profile.academy != user_academy:
                                    raise serializers.ValidationError(
                                        "You can only create bookings for users in your academy."
                                    )
                            else:
                                raise serializers.ValidationError(
                                    "The specified user does not belong to any academy."
                                )
                        else:
                            raise serializers.ValidationError(
                                "You are not associated with any academy."
                            )
            else:
                # For regular users, ensure they can only book for themselves
                if booked_by and booked_by != user:
                    raise serializers.ValidationError(
                        "You can only create bookings for yourself."
                    )

        # Basic time validation
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError("End time must be after start time.")

            # Check minimum booking duration (1 hour)
            duration = end_time - start_time
            if duration < timedelta(hours=1):
                raise serializers.ValidationError("Minimum booking duration is 1 hour.")

            # Check maximum booking duration (8 hours)
            if duration > timedelta(hours=8):
                raise serializers.ValidationError(
                    "Maximum booking duration is 8 hours."
                )

            # Check if booking is in the future
            if start_time <= timezone.now():
                raise serializers.ValidationError(
                    "Booking start time must be in the future."
                )

            # Check if booking is within reasonable future (3 months)
            if start_time > timezone.now() + timedelta(days=90):
                raise serializers.ValidationError(
                    "Bookings can only be made up to 3 months in advance."
                )

        # Field availability validation
        if field and start_time and end_time:
            if not field.is_available or not field.is_active:
                raise serializers.ValidationError(
                    "This field is not available for booking."
                )

            # Check for conflicts with existing bookings
            conflict_bookings = self._check_booking_conflicts(
                field, start_time, end_time
            )
            if conflict_bookings:
                raise serializers.ValidationError(
                    f"Time conflict detected. This field is already booked "
                    f"from {conflict_bookings[0].start_time} to "
                    f"{conflict_bookings[0].end_time}."
                )

        return data

    def _check_booking_conflicts(self, field, start_time, end_time):
        """
        Check for booking conflicts with existing bookings.
        """
        # Exclude current booking if updating
        queryset = FieldBooking.objects.filter(field=field)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        # Check for overlapping bookings
        conflicts = queryset.filter(
            Q(status__in=["confirmed", "pending"])
            & (
                # New booking starts during existing booking
                Q(start_time__lte=start_time, end_time__gt=start_time)
                # New booking ends during existing booking
                | Q(start_time__lt=end_time, end_time__gte=end_time)
                # New booking completely contains existing booking
                | Q(start_time__gte=start_time, end_time__lte=end_time)
                # Existing booking completely contains new booking
                | Q(start_time__lte=start_time, end_time__gte=end_time)
            )
        )

        return conflicts

    def create(self, validated_data):
        """
        Create a new booking with automatic cost calculation.
        """
        field = validated_data["field"]
        start_time = validated_data["start_time"]
        end_time = validated_data["end_time"]

        # Get the user who should be booked_by
        request = self.context.get("request")
        if request and request.user:
            user = request.user
            # If booked_by is provided and user is admin, use it
            if (
                user.user_type in ["academy_admin", "system_admin"]
                and "booked_by" in validated_data
            ):
                booked_by = validated_data["booked_by"]
            else:
                # Otherwise, use the requesting user
                booked_by = user
        else:
            booked_by = validated_data.get("booked_by")

        # Calculate duration and total cost
        duration = end_time - start_time
        hours = duration.total_seconds() / 3600
        total_cost = Decimal(str(hours)) * field.hourly_rate

        validated_data["total_cost"] = total_cost
        validated_data["booked_by"] = booked_by

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update booking with automatic cost recalculation if time changes.
        """
        field = validated_data.get("field", instance.field)
        start_time = validated_data.get("start_time", instance.start_time)
        end_time = validated_data.get("end_time", instance.end_time)

        # Recalculate cost if time or field changes
        if (
            "start_time" in validated_data
            or "end_time" in validated_data
            or "field" in validated_data
        ):
            duration = end_time - start_time
            hours = duration.total_seconds() / 3600
            validated_data["total_cost"] = Decimal(str(hours)) * field.hourly_rate

        return super().update(instance, validated_data)


class BookingAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for checking field availability.
    """

    field_id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    def validate(self, data):
        """Validate availability check request."""
        if data["end_time"] <= data["start_time"]:
            raise serializers.ValidationError("End time must be after start time.")
        return data


class BookingStatisticsSerializer(serializers.Serializer):
    """
    Serializer for booking statistics.
    """

    total_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_booking_duration = serializers.FloatField()
    most_popular_field = serializers.CharField()
    busiest_day = serializers.CharField()
