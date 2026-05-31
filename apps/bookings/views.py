from drf_spectacular.utils import extend_schema, extend_schema_view
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import AvailabilitySlot, Booking
from .serializers import (
    AvailabilitySlotSerializer,
    BookingCreateSerializer,
    BookingSerializer,
)
from .services import cancel_booking, create_booking
from apps.core.openapi import (
    AVAIL_CREATE,
    AVAIL_DELETE,
    AVAIL_GET,
    AVAIL_LIST,
    AVAIL_PATCH,
    AVAIL_UPDATE,
    BOOKINGS_CANCEL,
    BOOKINGS_CREATE,
    BOOKINGS_GET,
    BOOKINGS_LIST,
)
from apps.core.permissions import AvailabilitySlotAccess, BookingRoleAccess
from apps.providers.models import ServiceProvider


@extend_schema_view(
    list=extend_schema(tags=["Availability"], summary=AVAIL_LIST),
    retrieve=extend_schema(tags=["Availability"], summary=AVAIL_GET),
    create=extend_schema(tags=["Availability"], summary=AVAIL_CREATE),
    update=extend_schema(tags=["Availability"], summary=AVAIL_UPDATE),
    partial_update=extend_schema(tags=["Availability"], summary=AVAIL_PATCH),
    destroy=extend_schema(tags=["Availability"], summary=AVAIL_DELETE),
)
class AvailabilitySlotViewSet(ModelViewSet):
    queryset = AvailabilitySlot.objects.select_related("provider", "provider__user").all()
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [AvailabilitySlotAccess]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["weekday", "start_time"]
    ordering = ["weekday", "start_time"]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            return self.queryset
        if getattr(user, "role", None) == "provider":
            return self.queryset.filter(provider__user=user)
        return self.queryset.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if getattr(user, "role", None) == "provider":
            provider = ServiceProvider.objects.filter(user=user).first()
            if provider is not None:
                context["provider"] = provider
        return context

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        weekday = self.request.query_params.get("weekday")
        if weekday is not None and str(weekday).isdigit():
            qs = qs.filter(weekday=int(weekday))
        provider_id = self.request.query_params.get("provider")
        if provider_id and getattr(self.request.user, "role", None) == "admin":
            qs = qs.filter(provider_id=provider_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        if role != "provider":
            raise PermissionDenied("Only providers can create availability slots via the API.")

        provider = ServiceProvider.objects.filter(user=user).first()
        if provider is None:
            raise PermissionDenied("Create a provider profile before adding availability.")
        serializer.save(provider=provider)

    def perform_update(self, serializer):
        role = getattr(self.request.user, "role", None)
        if role == "provider":
            serializer.save(provider=serializer.instance.provider)
            return
        if role == "admin":
            serializer.save()
            return
        raise PermissionDenied("Only providers or administrators can update availability slots.")


@extend_schema_view(
    list=extend_schema(tags=["Bookings"], summary=BOOKINGS_LIST),
    retrieve=extend_schema(tags=["Bookings"], summary=BOOKINGS_GET),
    create=extend_schema(tags=["Bookings"], summary=BOOKINGS_CREATE),
)
class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.select_related("client", "provider", "service").all()
    serializer_class = BookingSerializer
    permission_classes = [BookingRoleAccess]
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["start_time", "created_at", "status"]
    ordering = ["-start_time"]

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "admin":
            return self.queryset
        if role == "provider":
            return self.queryset.filter(provider__user=user)
        return self.queryset.filter(client=user)

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        from_raw = self.request.query_params.get("from")
        to_raw = self.request.query_params.get("to")
        from_dt = to_dt = None
        if from_raw:
            from_dt = parse_datetime(from_raw)
            if from_dt and timezone.is_naive(from_dt):
                from_dt = timezone.make_aware(from_dt, timezone.get_current_timezone())
        if to_raw:
            to_dt = parse_datetime(to_raw)
            if to_dt and timezone.is_naive(to_dt):
                to_dt = timezone.make_aware(to_dt, timezone.get_current_timezone())
        if from_dt and to_dt:
            qs = qs.filter(start_time__lt=to_dt, end_time__gt=from_dt)
        elif from_dt:
            qs = qs.filter(end_time__gt=from_dt)
        elif to_dt:
            qs = qs.filter(start_time__lt=to_dt)
        return qs

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "client":
            raise PermissionDenied("Only clients can create bookings")

        input_serializer = BookingCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            booking = create_booking(
                client=request.user,
                provider=input_serializer.validated_data["provider"],
                service=input_serializer.validated_data["service"],
                start_time=input_serializer.validated_data["start_time"],
                note=input_serializer.validated_data.get("note", ""),
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        output_serializer = BookingSerializer(booking, context=self.get_serializer_context())
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Bookings"], summary=BOOKINGS_CANCEL)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        try:
            cancel_booking(booking=booking, actor=request.user)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(self.get_serializer(booking).data)
