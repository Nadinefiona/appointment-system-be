from django.db import transaction

from .models import Booking


@transaction.atomic
def create_booking(*, client, provider, service, start_time, end_time):
    existing = (
        Booking.objects.select_for_update()
        .filter(provider=provider, start_time=start_time, status=Booking.STATUS_BOOKED)
        .exists()
    )
    if existing:
        raise ValueError("Slot already booked")

    return Booking.objects.create(
        client=client,
        provider=provider,
        service=service,
        start_time=start_time,
        end_time=end_time,
    )
