from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.bookings.models import Booking


def _notifications_enabled() -> bool:
    return bool(getattr(settings, "EMAIL_NOTIFICATIONS_ENABLED", True))


def _format_when(start, end) -> str:
    start_local = timezone.localtime(start)
    end_local = timezone.localtime(end)
    date_part = start_local.strftime("%A, %d %B %Y")
    start_part = start_local.strftime("%H:%M")
    end_part = end_local.strftime("%H:%M")
    return f"{date_part}, {start_part}–{end_part}"


def _display_name(user) -> str:
    name = user.get_full_name().strip()
    if name:
        return name
    return user.email or user.get_username()


def _booking_email_context(booking: Booking) -> dict:
    provider_user = booking.provider.user
    when = _format_when(booking.start_time, booking.end_time)
    return {
        "client_name": _display_name(booking.client),
        "client_email": booking.client.email,
        "provider_name": _display_name(provider_user),
        "provider_email": provider_user.email,
        "service_name": booking.service.name,
        "when": when,
    }


def _send_templated_mail(*, subject: str, template_name: str, context: dict, recipients: list[str]) -> int:
    recipients = [email for email in recipients if email]
    if not recipients:
        return 0

    text_body = render_to_string(f"emails/{template_name}.txt", context)
    html_body = render_to_string(f"emails/{template_name}.html", context)
    return send_mail(
        subject=subject,
        message=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=settings.EMAIL_FAIL_SILENTLY,
        html_message=html_body,
    )


def _get_booking(booking_id) -> Booking:
    return Booking.objects.select_related(
        "client",
        "provider",
        "provider__user",
        "service",
    ).get(pk=booking_id)


def send_booking_confirmation(booking_id):
    if not _notifications_enabled():
        return 0

    booking = _get_booking(booking_id)
    if booking.status != Booking.STATUS_BOOKED:
        return 0

    context = _booking_email_context(booking)
    recipients = [booking.client.email, booking.provider.user.email]
    return _send_templated_mail(
        subject=f"Appointment confirmed: {context['service_name']}",
        template_name="booking_confirmation",
        context=context,
        recipients=recipients,
    )


def send_booking_cancellation(booking_id):
    if not _notifications_enabled():
        return 0

    booking = _get_booking(booking_id)
    if booking.status != Booking.STATUS_CANCELLED:
        return 0

    context = _booking_email_context(booking)
    recipients = [booking.client.email, booking.provider.user.email]
    return _send_templated_mail(
        subject=f"Appointment cancelled: {context['service_name']}",
        template_name="booking_cancellation",
        context=context,
        recipients=recipients,
    )


def send_booking_reminder(booking_id):
    if not _notifications_enabled():
        return 0

    booking = _get_booking(booking_id)
    if booking.status != Booking.STATUS_BOOKED or booking.reminder_sent_at is not None:
        return 0

    if not booking.client.email:
        return 0

    context = _booking_email_context(booking)
    sent = _send_templated_mail(
        subject=f"Reminder: {context['service_name']} on {context['when'].split(',')[0]}",
        template_name="booking_reminder",
        context=context,
        recipients=[booking.client.email],
    )
    return sent
