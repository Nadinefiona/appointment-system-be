from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.bookings.models import AvailabilitySlot, Booking
from apps.bookings.openings import day_openings_payload
from apps.bookings.serializers import AvailabilitySlotSerializer, BookingSummarySerializer
from apps.core.permissions import IsAdminOrAuthenticatedReadOnly
from apps.services.models import ServiceType

from .models import ServiceProvider
from .serializers import ServiceProviderSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Providers"],
        summary="List providers",
        description="Public catalog for authenticated users. Admins may create new provider records; others are read-only.",
    ),
    retrieve=extend_schema(
        tags=["Providers"],
        summary="Get provider",
        description="Fetch one provider by id (linked user, bio, buffer).",
    ),
    create=extend_schema(
        tags=["Providers"],
        summary="Create provider (admin)",
        description="Admin-only: create a **ServiceProvider** linked to an existing user.",
    ),
    update=extend_schema(tags=["Providers"], summary="Replace provider (admin)"),
    partial_update=extend_schema(tags=["Providers"], summary="Patch provider (admin)"),
    destroy=extend_schema(tags=["Providers"], summary="Delete provider (admin)"),
)
class ServiceProviderViewSet(ModelViewSet):
    queryset = ServiceProvider.objects.select_related("user").all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAuthenticatedReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["buffer_time"]
    ordering = ["buffer_time"]
    search_fields = ["user__username", "bio"]

    @extend_schema(
        tags=["Providers"],
        summary="Provider schedule in a time range",
        description=(
            "Returns recurring **availability** rows plus **booked/completed** bookings in `[from, to)` "
            "(ISO datetimes). **Provider** may only query their own id; **admin** any id. **Clients** should use "
            "**openings** instead (this response may include client identifiers)."
        ),
        parameters=[
            OpenApiParameter(
                name="from",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Inclusive range start (ISO 8601 datetime).",
            ),
            OpenApiParameter(
                name="to",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Exclusive range end (ISO 8601 datetime).",
            ),
        ],
    )
    @action(detail=True, methods=["get"], url_path="schedule")
    def schedule(self, request, pk=None):
        provider = self.get_object()
        role = getattr(request.user, "role", None)
        if role == "provider" and provider.user_id != request.user.id:
            raise PermissionDenied("You can only view your own schedule.")
        if role == "client":
            raise PermissionDenied("Use openings for public availability; schedule includes client details.")
        from_raw = request.query_params.get("from")
        to_raw = request.query_params.get("to")
        if not from_raw or not to_raw:
            raise ValidationError({"from": "This field is required.", "to": "This field is required."})

        from_dt = parse_datetime(from_raw)
        to_dt = parse_datetime(to_raw)
        if not from_dt or not to_dt:
            raise ValidationError("Enter valid ISO datetimes for from and to.")

        if timezone.is_naive(from_dt):
            from_dt = timezone.make_aware(from_dt, timezone.get_current_timezone())
        if timezone.is_naive(to_dt):
            to_dt = timezone.make_aware(to_dt, timezone.get_current_timezone())

        if from_dt >= to_dt:
            raise ValidationError("from must be before to.")

        slots = AvailabilitySlot.objects.filter(provider=provider).order_by("weekday", "start_time")
        bookings = (
            Booking.objects.filter(provider=provider)
            .filter(Q(status=Booking.STATUS_BOOKED) | Q(status=Booking.STATUS_COMPLETED))
            .filter(start_time__lt=to_dt, end_time__gt=from_dt)
            .select_related("service", "client")
            .order_by("start_time")
        )

        return Response(
            {
                "from": from_dt.isoformat(),
                "to": to_dt.isoformat(),
                "availability": AvailabilitySlotSerializer(slots, many=True).data,
                "bookings": BookingSummarySerializer(bookings, many=True).data,
            }
        )

    @extend_schema(
        tags=["Providers"],
        summary="Suggested openings for one calendar day",
        description=(
            "For a given **date** (provider local calendar day), returns weekly windows, busy intervals, "
            "and optional **suggested_starts** when `service` id is passed (15-minute grid; still validate on booking)."
        ),
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Calendar day `YYYY-MM-DD` (interpreted in server timezone for window math).",
            ),
            OpenApiParameter(
                name="service",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Service type id belonging to this provider; enables suggested start times.",
            ),
        ],
    )
    @action(detail=True, methods=["get"], url_path="openings")
    def openings(self, request, pk=None):
        provider = self.get_object()
        date_raw = request.query_params.get("date")
        if not date_raw:
            raise ValidationError({"date": "This field is required."})

        on_date = parse_date(date_raw)
        if not on_date:
            raise ValidationError({"date": "Enter a valid date."})

        service_duration = None
        service_id = request.query_params.get("service")
        if service_id:
            svc = ServiceType.objects.filter(pk=service_id, provider=provider).first()
            if svc is None:
                raise ValidationError({"service": "No matching service for this provider."})
            service_duration = svc.duration

        return Response(day_openings_payload(provider=provider, on_date=on_date, service_duration_minutes=service_duration))
