from django.db import transaction


def schedule_booking_confirmation(booking_id):
    def _send():
        from apps.bookings.emails import send_booking_confirmation

        send_booking_confirmation(booking_id)

    transaction.on_commit(_send)
