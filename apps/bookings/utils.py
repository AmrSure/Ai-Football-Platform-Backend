"""Utilities for the bookings app.

This module contains email services, notification utilities, and helper functions
for the booking system.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Field, FieldBooking

logger = logging.getLogger(__name__)


class BookingEmailService:
    """
    Service class for handling booking-related email notifications.
    """

    @staticmethod
    def send_booking_created_email(booking: FieldBooking):
        """
        Send email notification when a new booking is created.
        """
        try:
            subject = f"Booking Confirmation - {booking.field.name}"

            context = {
                "user_name": booking.booked_by.get_full_name()
                or booking.booked_by.email,
                "booking": booking,
                "field": booking.field,
                "academy": booking.field.academy,
                "booking_url": f"{settings.FRONTEND_URL}/bookings/{booking.id}"
                if hasattr(settings, "FRONTEND_URL")
                else None,
            }

            # Render HTML email
            html_message = render_to_string(
                "bookings/emails/booking_created.html", context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.booked_by.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(
                f"Booking created email sent to {booking.booked_by.email} for booking {booking.id}"
            )

        except Exception as e:
            logger.error(f"Failed to send booking created email: {str(e)}")

    @staticmethod
    def send_booking_confirmed_email(booking: FieldBooking):
        """
        Send email notification when a booking is confirmed.
        """
        try:
            subject = f"Booking Confirmed - {booking.field.name}"

            context = {
                "user_name": booking.booked_by.get_full_name()
                or booking.booked_by.email,
                "booking": booking,
                "field": booking.field,
                "academy": booking.field.academy,
                "booking_url": f"{settings.FRONTEND_URL}/bookings/{booking.id}"
                if hasattr(settings, "FRONTEND_URL")
                else None,
            }

            html_message = render_to_string(
                "bookings/emails/booking_confirmed.html", context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.booked_by.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(
                f"Booking confirmed email sent to {booking.booked_by.email} for booking {booking.id}"
            )

        except Exception as e:
            logger.error(f"Failed to send booking confirmed email: {str(e)}")

    @staticmethod
    def send_booking_cancelled_email(
        booking: FieldBooking, cancelled_by_admin: bool = False
    ):
        """
        Send email notification when a booking is cancelled.
        """
        try:
            if cancelled_by_admin:
                subject = f"Booking Cancelled by Academy - {booking.field.name}"
            else:
                subject = f"Booking Cancelled - {booking.field.name}"

            context = {
                "user_name": booking.booked_by.get_full_name()
                or booking.booked_by.email,
                "booking": booking,
                "field": booking.field,
                "academy": booking.field.academy,
                "cancelled_by_admin": cancelled_by_admin,
                "booking_url": f"{settings.FRONTEND_URL}/bookings/{booking.id}"
                if hasattr(settings, "FRONTEND_URL")
                else None,
            }

            html_message = render_to_string(
                "bookings/emails/booking_cancelled.html", context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.booked_by.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(
                f"Booking cancelled email sent to {booking.booked_by.email} for booking {booking.id}"
            )

        except Exception as e:
            logger.error(f"Failed to send booking cancelled email: {str(e)}")

    @staticmethod
    def send_booking_reminder_email(booking: FieldBooking):
        """
        Send email reminder before booking start time.
        """
        try:
            subject = f"Booking Reminder - {booking.field.name}"

            context = {
                "user_name": booking.booked_by.get_full_name()
                or booking.booked_by.email,
                "booking": booking,
                "field": booking.field,
                "academy": booking.field.academy,
                "booking_url": f"{settings.FRONTEND_URL}/bookings/{booking.id}"
                if hasattr(settings, "FRONTEND_URL")
                else None,
            }

            html_message = render_to_string(
                "bookings/emails/booking_reminder.html", context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.booked_by.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(
                f"Booking reminder email sent to {booking.booked_by.email} for booking {booking.id}"
            )

        except Exception as e:
            logger.error(f"Failed to send booking reminder email: {str(e)}")

    @staticmethod
    def send_booking_completed_email(booking: FieldBooking):
        """
        Send email notification when a booking is completed.
        """
        try:
            subject = f"Booking Completed - {booking.field.name}"

            context = {
                "user_name": booking.booked_by.get_full_name()
                or booking.booked_by.email,
                "booking": booking,
                "field": booking.field,
                "academy": booking.field.academy,
                "booking_url": f"{settings.FRONTEND_URL}/bookings/{booking.id}"
                if hasattr(settings, "FRONTEND_URL")
                else None,
            }

            html_message = render_to_string(
                "bookings/emails/booking_completed.html", context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.booked_by.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(
                f"Booking completed email sent to {booking.booked_by.email} for booking {booking.id}"
            )

        except Exception as e:
            logger.error(f"Failed to send booking completed email: {str(e)}")

    @staticmethod
    def notify_academy_admin_new_booking(booking: FieldBooking):
        """
        Send email notification to academy admin about new booking.
        """
        try:
            # Get academy admin email
            academy_admin = booking.field.academy.admins.filter(is_active=True).first()
            if not academy_admin or not academy_admin.user.email:
                logger.warning(
                    f"No academy admin email found for academy {booking.field.academy.name}"
                )
                return

            subject = f"New Booking Received - {booking.field.name}"

            context = {
                "admin_name": academy_admin.user.get_full_name()
                or academy_admin.user.email,
                "booking": booking,
                "field": booking.field,
                "academy": booking.field.academy,
                "customer": booking.booked_by,
                "admin_url": f"{settings.ADMIN_URL}/bookings/{booking.id}"
                if hasattr(settings, "ADMIN_URL")
                else None,
            }

            html_message = render_to_string(
                "bookings/emails/admin_new_booking.html", context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[academy_admin.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(
                f"New booking notification sent to academy admin {academy_admin.user.email}"
            )

        except Exception as e:
            logger.error(f"Failed to send new booking notification to admin: {str(e)}")


class BookingConflictChecker:
    """
    Utility class for checking booking conflicts and availability.
    """

    @staticmethod
    def check_field_availability(
        field: Field,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: int = None,
    ) -> Dict:
        """
        Check if a field is available for the given time period.

        Returns:
            dict: {
                'available': bool,
                'conflicts': list of conflicting bookings,
                'suggestions': list of available time slots
            }
        """
        # Check if field is active and available
        if not field.is_active or not field.is_available:
            return {
                "available": False,
                "conflicts": [],
                "suggestions": [],
                "reason": "Field is not available for booking",
            }

        # Get conflicting bookings
        conflicts_queryset = FieldBooking.objects.filter(
            field=field, status__in=["confirmed", "pending"]
        ).filter(start_time__lt=end_time, end_time__gt=start_time)

        if exclude_booking_id:
            conflicts_queryset = conflicts_queryset.exclude(id=exclude_booking_id)

        conflicts = list(conflicts_queryset)

        if conflicts:
            # Generate alternative time suggestions
            suggestions = BookingConflictChecker._generate_time_suggestions(
                field, start_time, end_time, conflicts
            )

            return {
                "available": False,
                "conflicts": conflicts,
                "suggestions": suggestions,
                "reason": "Time slot conflicts with existing bookings",
            }

        return {
            "available": True,
            "conflicts": [],
            "suggestions": [],
            "reason": "Field is available for the requested time",
        }

    @staticmethod
    def _generate_time_suggestions(
        field: Field,
        start_time: datetime,
        end_time: datetime,
        conflicts: List[FieldBooking],
    ) -> List[Dict]:
        """
        Generate alternative time slot suggestions when there are conflicts.
        """
        suggestions = []
        duration = end_time - start_time

        # Get all bookings for the day to find gaps
        day_start = start_time.replace(hour=8, minute=0, second=0, microsecond=0)
        day_end = start_time.replace(hour=22, minute=0, second=0, microsecond=0)

        day_bookings = FieldBooking.objects.filter(
            field=field,
            status__in=["confirmed", "pending"],
            start_time__date=start_time.date(),
        ).order_by("start_time")

        # Find available gaps
        current_time = day_start
        for booking in day_bookings:
            # Check if there's a gap before this booking
            if (
                booking.start_time > current_time
                and (booking.start_time - current_time) >= duration
            ):
                suggestions.append(
                    {
                        "start_time": current_time.isoformat(),
                        "end_time": (current_time + duration).isoformat(),
                        "duration_hours": duration.total_seconds() / 3600,
                    }
                )

                if len(suggestions) >= 3:  # Limit to 3 suggestions
                    break

            current_time = max(current_time, booking.end_time)

        # Check if there's time after the last booking
        if current_time + duration <= day_end and len(suggestions) < 3:
            suggestions.append(
                {
                    "start_time": current_time.isoformat(),
                    "end_time": (current_time + duration).isoformat(),
                    "duration_hours": duration.total_seconds() / 3600,
                }
            )

        return suggestions


class BookingStatisticsCalculator:
    """
    Utility class for calculating booking statistics.
    """

    @staticmethod
    def get_academy_booking_stats(
        academy_id: int, start_date: datetime = None, end_date: datetime = None
    ) -> Dict:
        """
        Calculate booking statistics for an academy.
        """
        from django.db.models import Avg, Count, Sum

        queryset = FieldBooking.objects.filter(field__academy_id=academy_id)

        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)

        stats = queryset.aggregate(
            total_bookings=Count("id"),
            total_revenue=Sum("total_cost"),
            average_cost=Avg("total_cost"),
        )

        # Status breakdown
        status_counts = {
            "confirmed": queryset.filter(status="confirmed").count(),
            "pending": queryset.filter(status="pending").count(),
            "cancelled": queryset.filter(status="cancelled").count(),
            "completed": queryset.filter(status="completed").count(),
        }

        # Most popular field
        popular_field = (
            queryset.values("field__name")
            .annotate(booking_count=Count("id"))
            .order_by("-booking_count")
            .first()
        )

        return {
            "total_bookings": stats["total_bookings"] or 0,
            "total_revenue": float(stats["total_revenue"] or 0),
            "average_cost": float(stats["average_cost"] or 0),
            "status_breakdown": status_counts,
            "most_popular_field": popular_field["field__name"]
            if popular_field
            else "N/A",
        }

    @staticmethod
    def get_field_utilization_rate(
        field: Field, start_date=None, end_date=None
    ) -> Dict:
        """
        Calculate field utilization rate.
        start_date and end_date can be datetime.date or datetime.datetime objects
        """
        queryset = field.bookings.filter(status__in=["confirmed", "completed"])

        if start_date:
            # Handle both date and datetime objects
            if hasattr(start_date, "date"):
                # It's a datetime object, use it directly
                queryset = queryset.filter(start_time__gte=start_date)
            else:
                # It's a date object, filter by date
                queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            # Handle both date and datetime objects
            if hasattr(end_date, "date"):
                # It's a datetime object, use it directly
                queryset = queryset.filter(start_time__lte=end_date)
            else:
                # It's a date object, filter by date
                queryset = queryset.filter(start_time__date__lte=end_date)

        # Calculate total booked hours
        total_booked_seconds = sum(
            (booking.end_time - booking.start_time).total_seconds()
            for booking in queryset
        )
        total_booked_hours = total_booked_seconds / 3600

        # Calculate available hours (assuming 14 hours per day, 8 AM to 10 PM)
        if start_date and end_date:
            # Handle both datetime.date and datetime.datetime objects
            if hasattr(start_date, "date"):
                start_date_obj = start_date.date()
            else:
                start_date_obj = start_date
            if hasattr(end_date, "date"):
                end_date_obj = end_date.date()
            else:
                end_date_obj = end_date
            days = (end_date_obj - start_date_obj).days + 1
        else:
            days = 30  # Default to 30 days

        total_available_hours = days * 14  # 14 hours per day

        utilization_rate = (
            (total_booked_hours / total_available_hours) * 100
            if total_available_hours > 0
            else 0
        )

        return {
            "total_booked_hours": round(total_booked_hours, 2),
            "total_available_hours": total_available_hours,
            "utilization_rate": round(utilization_rate, 2),
            "booking_count": queryset.count(),
        }
