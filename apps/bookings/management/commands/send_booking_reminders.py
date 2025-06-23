"""Management command to send booking reminders.

This command can be run as a cron job to automatically send reminder emails
to customers about their upcoming bookings.
"""

import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.models import FieldBooking
from apps.bookings.utils import BookingEmailService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send booking reminder emails for upcoming bookings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Send reminders for bookings starting in X hours (default: 24)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be sent without actually sending emails",
        )

    def handle(self, *args, **options):
        hours_ahead = options["hours"]
        dry_run = options["dry_run"]

        # Calculate time range for reminders
        now = timezone.now()
        reminder_start = now + timedelta(hours=hours_ahead - 1)
        reminder_end = now + timedelta(hours=hours_ahead)

        self.stdout.write(
            self.style.SUCCESS(
                f"Looking for bookings between {reminder_start} and {reminder_end}"
            )
        )

        # Find confirmed bookings that need reminders
        bookings_needing_reminders = FieldBooking.objects.filter(
            status="confirmed",
            start_time__gte=reminder_start,
            start_time__lt=reminder_end,
        ).select_related("field", "field__academy", "booked_by")

        reminder_count = 0
        error_count = 0

        for booking in bookings_needing_reminders:
            try:
                if dry_run:
                    self.stdout.write(
                        f"Would send reminder for booking {booking.id} to {booking.booked_by.email}"
                    )
                else:
                    BookingEmailService.send_booking_reminder_email(booking)
                    self.stdout.write(
                        f"Sent reminder for booking {booking.id} to {booking.booked_by.email}"
                    )

                reminder_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to send reminder for booking {booking.id}: {str(e)}"
                    )
                )
                logger.error(
                    f"Failed to send reminder for booking {booking.id}: {str(e)}"
                )

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dry run complete. Would send {reminder_count} reminders."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sent {reminder_count} reminder emails successfully."
                )
            )

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f"{error_count} reminders failed to send.")
            )
