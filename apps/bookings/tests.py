from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.bookings.emails import (
    send_booking_cancellation,
    send_booking_confirmation,
    send_booking_reminder,
)
from apps.bookings.models import AvailabilitySlot, Booking
from apps.bookings.openings import day_openings_payload
from apps.bookings.services import cancel_booking, create_booking
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
        self.service = ServiceType.objects.create(name="Consultation")
        self.service.providers.add(self.provider)
        tz = timezone.get_current_timezone()
        booking_date = timezone.localdate() + timedelta(days=2)
        AvailabilitySlot.objects.create(
            provider=self.provider,
            weekday=booking_date.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.start_time = timezone.make_aware(datetime.combine(booking_date, time(10, 0)), tz)

    def _create_booking(self, note=""):
        return create_booking(
            client=self.client_user,
            provider=self.provider,
            service=self.service,
            start_time=self.start_time,
            note=note,
        )

    def test_create_booking_with_note_computes_end_time(self):
        booking = self._create_booking(note="Running late")
        self.assertEqual(booking.note, "Running late")
        self.assertGreater(booking.end_time, booking.start_time)

    def test_client_cannot_double_book_same_time(self):
        self._create_booking()
        client_api = APIClient()
        client_api.force_authenticate(user=self.client_user)
        response = client_api.post(
            "/api/bookings/",
            {
                "provider": str(self.provider.pk),
                "service": str(self.service.pk),
                "start_time": self.start_time.isoformat().replace("+00:00", "Z"),
                "note": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertIn("Consultation", mail.outbox[0].body)

    def test_confirmation_skipped_when_notifications_disabled(self):
        with override_settings(EMAIL_NOTIFICATIONS_ENABLED=False):
            booking = self._create_booking()
            sent = send_booking_confirmation(booking.pk)
        self.assertEqual(sent, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_command_sends_once(self):
        booking = self._create_booking()
        booking.start_time = timezone.now() + timedelta(hours=24)
        booking.end_time = booking.start_time + timedelta(minutes=60)
        booking.save(update_fields=["start_time", "end_time"])

        call_command("send_booking_reminders")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reminder", mail.outbox[0].subject)

        booking.refresh_from_db()
        self.assertIsNotNone(booking.reminder_sent_at)

        mail.outbox.clear()
        call_command("send_booking_reminders")
        self.assertEqual(len(mail.outbox), 0)

    def test_can_rebook_same_slot_after_cancel(self):
        booking = self._create_booking()
        cancel_booking(booking=booking, actor=self.client_user)
        booking2 = self._create_booking()
        self.assertEqual(booking2.status, Booking.STATUS_BOOKED)
        self.assertNotEqual(booking.pk, booking2.pk)

    def test_cancellation_email_sent(self):
        booking = self._create_booking()
        cancel_booking(booking=booking, actor=self.client_user)
        mail.outbox.clear()
        sent = send_booking_cancellation(booking.pk)
        self.assertEqual(sent, 1)
        self.assertIn("cancelled", mail.outbox[0].subject.lower())

    def test_openings_available_times_default_duration(self):
        on_date = timezone.localdate(self.start_time)
        payload = day_openings_payload(provider=self.provider, on_date=on_date)
        self.assertGreater(len(payload["available_times"]), 0)
        self.assertEqual(payload["available_times"][0]["value"], payload["suggested_starts"][0])

    def test_booking_list_includes_service_and_provider_names(self):
        booking = self._create_booking()
        api = APIClient()
        api.force_authenticate(user=self.client_user)
        response = api.get("/api/bookings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data["results"][0]
        self.assertEqual(item["service"]["name"], "Consultation")
        self.assertEqual(item["provider"]["email"], "provider@example.com")

    def test_booking_with_excessive_buffer_time_does_not_crash(self):
        self.provider.buffer_time = 2147483647
        self.provider.save(update_fields=["buffer_time"])
        booking = self._create_booking()
        self.assertEqual(booking.status, Booking.STATUS_BOOKED)

    def test_reminder_not_sent_for_cancelled_booking(self):
        booking = self._create_booking()
        booking.start_time = timezone.now() + timedelta(hours=24)
        booking.end_time = booking.start_time + timedelta(minutes=60)
        booking.status = Booking.STATUS_CANCELLED
        booking.save()

        sent = send_booking_reminder(booking.pk)
        self.assertEqual(sent, 0)


class AvailabilitySlotApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.provider_user = User.objects.create_user(
            username="provider",
            email="provider@example.com",
            password="pass",
            role=User.ROLE_PROVIDER,
        )
        self.provider = ServiceProvider.objects.create(user=self.provider_user)
        self.api.force_authenticate(user=self.provider_user)
        AvailabilitySlot.objects.create(
            provider=self.provider,
            weekday=1,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )

    def test_rejects_overlapping_create(self):
        response = self.api.post(
            "/api/availability-slots/",
            {"weekday": 1, "start_time": "11:00:00", "end_time": "13:00:00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_allows_non_overlapping_create(self):
        response = self.api.post(
            "/api/availability-slots/",
            {"weekday": 1, "start_time": "13:00:00", "end_time": "17:00:00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_edit_slot(self):
        slot = AvailabilitySlot.objects.get(provider=self.provider, weekday=1)
        response = self.api.patch(
            f"/api/availability-slots/{slot.pk}/",
            {"start_time": "08:00:00", "end_time": "10:00:00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slot.refresh_from_db()
        self.assertEqual(str(slot.start_time), "08:00:00")
