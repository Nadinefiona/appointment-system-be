from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.bookings.emails import send_booking_confirmation, send_booking_reminder
from apps.bookings.models import AvailabilitySlot, Booking
from apps.bookings.services import create_booking
from apps.providers.models import ServiceProvider
from apps.services.models import ServiceType

User = get_user_model()

EMAIL_TEST_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "EMAIL_NOTIFICATIONS_ENABLED": True,
    "EMAIL_FAIL_SILENTLY": False,
    "DEFAULT_FROM_EMAIL": "test@appointments.local",
    "BOOKING_REMINDER_HOURS": 24,
    "BOOKING_REMINDER_WINDOW_MINUTES": 60,
}


@override_settings(**EMAIL_TEST_SETTINGS)
class BookingEmailTests(TestCase):
    def setUp(self):
        mail.outbox.clear()
        self.client_user = User.objects.create_user(
            username="client1",
            email="client@example.com",
            password="pass",
            role=User.ROLE_CLIENT,
        )
        self.provider_user = User.objects.create_user(
            username="provider1",
            email="provider@example.com",
            password="pass",
            role=User.ROLE_PROVIDER,
        )
        self.provider = ServiceProvider.objects.create(user=self.provider_user, buffer_time=0)
        self.service = ServiceType.objects.create(
            provider=self.provider,
            name="Consultation",
            duration=60,
            price="50.00",
        )
        tz = timezone.get_current_timezone()
        booking_date = timezone.localdate() + timedelta(days=2)
        AvailabilitySlot.objects.create(
            provider=self.provider,
            weekday=booking_date.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.start_time = timezone.make_aware(datetime.combine(booking_date, time(10, 0)), tz)

    def _create_booking(self):
        return create_booking(
            client=self.client_user,
            provider=self.provider,
            service=self.service,
            start_time=self.start_time,
        )

    def test_confirmation_email_sent_to_client_and_provider(self):
        booking = self._create_booking()
        sent = send_booking_confirmation(booking.pk)
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(set(message.to), {"client@example.com", "provider@example.com"})
        self.assertIn("Consultation", message.subject)
        self.assertIn("confirmed", message.body.lower())

    def test_confirmation_scheduled_on_commit(self):
        with self.captureOnCommitCallbacks(execute=True):
            booking = self._create_booking()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(str(booking.id), mail.outbox[0].body)

    def test_confirmation_skipped_when_notifications_disabled(self):
        with override_settings(EMAIL_NOTIFICATIONS_ENABLED=False):
            booking = self._create_booking()
            sent = send_booking_confirmation(booking.pk)
        self.assertEqual(sent, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_command_sends_once(self):
        booking = self._create_booking()
        booking.start_time = timezone.now() + timedelta(hours=24)
        booking.end_time = booking.start_time + timedelta(minutes=self.service.duration)
        booking.save(update_fields=["start_time", "end_time"])

        call_command("send_booking_reminders")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reminder", mail.outbox[0].subject)

        booking.refresh_from_db()
        self.assertIsNotNone(booking.reminder_sent_at)

        mail.outbox.clear()
        call_command("send_booking_reminders")
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_not_sent_for_cancelled_booking(self):
        booking = self._create_booking()
        booking.start_time = timezone.now() + timedelta(hours=24)
        booking.end_time = booking.start_time + timedelta(minutes=self.service.duration)
        booking.status = Booking.STATUS_CANCELLED
        booking.save()

        sent = send_booking_reminder(booking.pk)
        self.assertEqual(sent, 0)
