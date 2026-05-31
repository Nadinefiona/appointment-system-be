from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone

from apps.bookings.models import AvailabilitySlot, Booking
from apps.providers.buffer import effective_buffer_minutes


def _default_slot_minutes():
    return int(getattr(settings, "BOOKING_DEFAULT_MINUTES", 60))


def _time_label(dt):
    return timezone.localtime(dt).strftime("%H:%M")


def _local_day_bounds(on_date):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(on_date, time.min), tz)
    end = timezone.make_aware(datetime.combine(on_date, time.max), tz)
    return start, end


def _intervals_overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def day_openings_payload(*, provider, on_date, slot_minutes=None):
    if slot_minutes is None:
        slot_minutes = _default_slot_minutes()

    weekday = on_date.weekday()
    day_start, day_end = _local_day_bounds(on_date)
    base_slots = AvailabilitySlot.objects.filter(provider=provider, weekday=weekday)

    windows = list(base_slots.order_by("start_time").values("start_time", "end_time"))

    booked = (
        Booking.objects.filter(provider=provider, status=Booking.STATUS_BOOKED)
        .filter(start_time__lt=day_end, end_time__gt=day_start)
        .order_by("start_time")
    )

    tz = timezone.get_current_timezone()
    buffer = timedelta(minutes=effective_buffer_minutes(provider.buffer_time))

    busy = []
    for b in booked:
        busy.append(
            {
                "start_time": timezone.localtime(b.start_time, tz).isoformat(),
                "end_time": timezone.localtime(b.end_time, tz).isoformat(),
            }
        )

    suggested_starts = []
    available_times = []
    duration = timedelta(minutes=int(slot_minutes))
    step = timedelta(minutes=15)

    for w in base_slots.order_by("start_time"):
        window_start = timezone.make_aware(datetime.combine(on_date, w.start_time), tz)
        window_end = timezone.make_aware(datetime.combine(on_date, w.end_time), tz)
        if window_end <= window_start:
            continue

        t = window_start
        while t + duration <= window_end:
            ok = True
            for b in booked:
                b_eff_start = b.start_time - buffer
                b_eff_end = b.end_time + buffer
                if _intervals_overlap(t, t + duration, b_eff_start, b_eff_end) or b.start_time == t:
                    ok = False
                    break
            if ok:
                local_t = timezone.localtime(t, tz)
                iso = local_t.isoformat()
                suggested_starts.append(iso)
                available_times.append({"value": iso, "label": _time_label(t)})
            t += step

    return {
        "date": on_date.isoformat(),
        "weekday": weekday,
        "duration_minutes": int(slot_minutes),
        "windows": [
            {
                "start_time": str(x["start_time"]),
                "end_time": str(x["end_time"]),
            }
            for x in windows
        ],
        "busy": busy,
        "suggested_starts": suggested_starts,
        "available_times": available_times,
    }
