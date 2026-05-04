from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone

from apps.bookings.models import AvailabilitySlot, Booking


def _local_day_bounds(on_date):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(on_date, time.min), tz)
    end = timezone.make_aware(datetime.combine(on_date, time.max), tz)
    return start, end


def _intervals_overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def day_openings_payload(*, provider, on_date, service_duration_minutes=None):
    weekday = on_date.weekday()
    day_start, day_end = _local_day_bounds(on_date)
    base_slots = AvailabilitySlot.objects.filter(provider=provider, weekday=weekday).filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=on_date),
        Q(valid_to__isnull=True) | Q(valid_to__gte=on_date),
    )

    windows = list(
        base_slots.order_by("start_time").values("start_time", "end_time", "valid_from", "valid_to")
    )

    booked = (
        Booking.objects.filter(provider=provider, status=Booking.STATUS_BOOKED)
        .filter(start_time__lt=day_end, end_time__gt=day_start)
        .order_by("start_time")
    )

    tz = timezone.get_current_timezone()
    buffer = timedelta(minutes=int(provider.buffer_time))

    busy = []
    for b in booked:
        busy.append(
            {
                "start_time": timezone.localtime(b.start_time, tz).isoformat(),
                "end_time": timezone.localtime(b.end_time, tz).isoformat(),
            }
        )

    suggested_starts = []
    if service_duration_minutes is not None:
        duration = timedelta(minutes=int(service_duration_minutes))
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
                    suggested_starts.append(timezone.localtime(t, tz).isoformat())
                t += step

    return {
        "date": on_date.isoformat(),
        "weekday": weekday,
        "windows": [
            {
                "start_time": str(x["start_time"]),
                "end_time": str(x["end_time"]),
                "valid_from": x["valid_from"].isoformat() if x["valid_from"] else None,
                "valid_to": x["valid_to"].isoformat() if x["valid_to"] else None,
            }
            for x in windows
        ],
        "busy": busy,
        "suggested_starts": suggested_starts,
    }
