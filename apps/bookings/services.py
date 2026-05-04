from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.bookings.models import AvailabilitySlot, Booking
from apps.providers.models import ServiceProvider


def _service_duration_end(*, start_at, service):
    return start_at + timedelta(minutes=int(service.duration))


def _fits_availability(*, provider, start_at, end_at):
    local = timezone.localtime(start_at)
    weekday = local.weekday()
    local_date = local.date()
    start_t = local.time()
    end_t = timezone.localtime(end_at).time()

    slots = AvailabilitySlot.objects.filter(provider=provider, weekday=weekday)
    for slot in slots:
        if slot.valid_from and local_date < slot.valid_from:
            continue
        if slot.valid_to and local_date > slot.valid_to:
            continue
        if slot.start_time <= start_t and slot.end_time >= end_t:
            return True
    return False


@transaction.atomic
def create_booking(*, client, provider, service, start_time, end_time=None):
    provider = ServiceProvider.objects.select_for_update().get(pk=provider.pk)

    if service.provider_id != provider.id:
        raise ValueError("Service does not belong to provider.")

    expected_end = _service_duration_end(start_at=start_time, service=service)
    if end_time is None:
        end_time = expected_end
    else:
        if end_time != expected_end:
            raise ValueError("Booking length must match service duration.")

    if end_time <= start_time:
        raise ValueError("Invalid booking interval.")

    if not _fits_availability(provider=provider, start_at=start_time, end_at=end_time):
        raise ValueError("Requested time is outside provider availability.")

    buffer = timedelta(minutes=int(provider.buffer_time))
    new_start_eff = start_time - buffer
    new_end_eff = end_time + buffer

    conflicts = (
        Booking.objects.select_for_update()
        .filter(provider=provider, status=Booking.STATUS_BOOKED)
        .filter(
            Q(start_time__lt=new_end_eff, end_time__gt=new_start_eff)
            | Q(start_time=start_time)
        )
    )
    if conflicts.exists():
        raise ValueError("Time conflicts with an existing booking.")

    return Booking.objects.create(
        client=client,
        provider=provider,
        service=service,
        start_time=start_time,
        end_time=end_time,
        status=Booking.STATUS_BOOKED,
    )


@transaction.atomic
def cancel_booking(*, booking, actor):
    booking = Booking.objects.select_for_update().get(pk=booking.pk)

    if booking.status != Booking.STATUS_BOOKED:
        raise ValueError("Only active bookings can be cancelled.")

    role = getattr(actor, "role", None)
    if role == "admin":
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=["status"])
        return booking

    if role == "client" and booking.client_id == actor.id:
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=["status"])
        return booking

    if role == "provider" and booking.provider.user_id == actor.id:
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=["status"])
        return booking

    raise PermissionDenied("Not allowed to cancel this booking.")
