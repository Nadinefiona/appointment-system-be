import logging

from django.db import transaction

logger = logging.getLogger(__name__)


def schedule_booking_confirmation(booking_id):
    def _enqueue():
        from apps.bookings.tasks import send_booking_confirmation_task

        try:
            send_booking_confirmation_task.delay(booking_id)
        except Exception:
            logger.exception("Failed to enqueue booking confirmation email for booking %s", booking_id)

    transaction.on_commit(_enqueue)


def schedule_booking_cancellation(booking_id):
    def _enqueue():
        from apps.bookings.tasks import send_booking_cancellation_task

        try:
            send_booking_cancellation_task.delay(booking_id)
        except Exception:
            logger.exception("Failed to enqueue booking cancellation email for booking %s", booking_id)

    transaction.on_commit(_enqueue)
