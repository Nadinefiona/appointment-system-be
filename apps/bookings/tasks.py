from celery import shared_task


@shared_task(
    name="bookings.send_booking_confirmation",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_booking_confirmation_task(self, booking_id):
    from apps.bookings.emails import send_booking_confirmation

    try:
        return send_booking_confirmation(booking_id)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
    name="bookings.send_booking_cancellation",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_booking_cancellation_task(self, booking_id):
    from apps.bookings.emails import send_booking_cancellation

    try:
        return send_booking_cancellation(booking_id)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
    name="bookings.send_booking_reminder",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_booking_reminder_task(self, booking_id):
    from apps.bookings.emails import send_booking_reminder

    try:
        return send_booking_reminder(booking_id)
    except Exception as exc:
        raise self.retry(exc=exc)
