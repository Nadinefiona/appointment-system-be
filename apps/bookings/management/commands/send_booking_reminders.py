from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.emails import send_booking_reminder
from apps.bookings.models import Booking


class Command(BaseCommand):
    help = (
        "Send reminder emails for booked appointments starting in about "
        "BOOKING_REMINDER_HOURS (default 24). Run on a schedule (cron, Task Scheduler)."
    )

    def handle(self, *args, **options):
        hours = settings.BOOKING_REMINDER_HOURS
        window = timedelta(minutes=settings.BOOKING_REMINDER_WINDOW_MINUTES)
        now = timezone.now()
        target = now + timedelta(hours=hours)
        window_start = target - window
        window_end = target + window

        candidates = (
            Booking.objects.filter(
                status=Booking.STATUS_BOOKED,
                reminder_sent_at__isnull=True,
                start_time__gte=window_start,
                start_time__lte=window_end,
            )
            .select_related("client", "provider", "provider__user", "service")
            .order_by("start_time")
        )

        sent_count = 0
        for booking in candidates:
            if send_booking_reminder(booking.pk):
                booking.reminder_sent_at = timezone.now()
                booking.save(update_fields=["reminder_sent_at"])
                sent_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Reminders sent: {sent_count} "
                f"(window {window_start.isoformat()} – {window_end.isoformat()})"
            )
        )
