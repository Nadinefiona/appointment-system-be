import logging
import threading

from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)


def _dispatch(task, email_fn_name, booking_id, label):
    """Send a booking email without ever blocking the HTTP request.

    - With a real Celery broker (worker running): hand off to the queue via .delay().
    - Without a broker (eager mode, e.g. free hosting): run the send in a daemon
      thread so the booking response returns immediately and email goes out later.
    """
    if settings.CELERY_TASK_ALWAYS_EAGER:
        def _run():
            from apps.bookings import emails

            try:
                getattr(emails, email_fn_name)(booking_id)
            except Exception:
                logger.exception("Failed to send %s email for booking %s", label, booking_id)

        if getattr(settings, "TESTING", False):
            _run()
        else:
            threading.Thread(target=_run, daemon=True).start()
        return

    try:
        task.delay(booking_id)
    except Exception:
        logger.exception("Failed to enqueue %s email for booking %s", label, booking_id)


def schedule_booking_confirmation(booking_id):
    def _send():
        from apps.bookings.tasks import send_booking_confirmation_task

        _dispatch(send_booking_confirmation_task, "send_booking_confirmation", booking_id, "confirmation")

    transaction.on_commit(_send)


def schedule_booking_cancellation(booking_id):
    def _send():
        from apps.bookings.tasks import send_booking_cancellation_task

        _dispatch(send_booking_cancellation_task, "send_booking_cancellation", booking_id, "cancellation")

    transaction.on_commit(_send)
