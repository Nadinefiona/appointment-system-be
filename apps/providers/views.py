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
from apps.core.openapi import (
    PROVIDERS_CREATE,
    PROVIDERS_DELETE,
    PROVIDERS_GET,
    PROVIDERS_LIST,
    PROVIDERS_OPENINGS,
    PROVIDERS_PATCH,
    PROVIDERS_SCHEDULE,
    PROVIDERS_UPDATE,
)
from apps.core.permissions import IsAdminOrAuthenticatedReadOnly
from .models import ServiceProvider
from .serializers import ServiceProviderSerializer


@extend_schema_view(
    list=extend_schema(tags=["Providers"], summary=PROVIDERS_LIST),
    retrieve=extend_schema(tags=["Providers"], summary=PROVIDERS_GET),
    create=extend_schema(tags=["Providers"], summary=PROVIDERS_CREATE),
    update=extend_schema(tags=["Providers"], summary=PROVIDERS_UPDATE),
    partial_update=extend_schema(tags=["Providers"], summary=PROVIDERS_PATCH),
    destroy=extend_schema(tags=["Providers"], summary=PROVIDERS_DELETE),
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
        summary=PROVIDERS_SCHEDULE,
        parameters=[
            OpenApiParameter(name="from", type=str, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="to", type=str, location=OpenApiParameter.QUERY, required=True),
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
        summary=PROVIDERS_OPENINGS,
        parameters=[
            OpenApiParameter(name="date", type=str, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(
                name="duration",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Appointment length in minutes (for suggested start times).",
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

        duration_raw = request.query_params.get("duration")
        slot_minutes = None
        if duration_raw is not None:
            if not str(duration_raw).isdigit() or int(duration_raw) <= 0:
                raise ValidationError({"duration": "Enter a positive number of minutes."})
            slot_minutes = int(duration_raw)

        return Response(
            day_openings_payload(provider=provider, on_date=on_date, slot_minutes=slot_minutes)
        )
