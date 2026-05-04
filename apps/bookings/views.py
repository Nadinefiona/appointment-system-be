from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import AvailabilitySlot, Booking
from .serializers import AvailabilitySlotSerializer, BookingSerializer
from .services import cancel_booking, create_booking
from apps.core.permissions import AvailabilitySlotAccess, BookingRoleAccess


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

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        weekday = self.request.query_params.get("weekday")
        if weekday is not None and str(weekday).isdigit():
            qs = qs.filter(weekday=int(weekday))
        provider_id = self.request.query_params.get("provider")
        if provider_id and getattr(self.request.user, "role", None) == "admin":
            qs = qs.filter(provider_id=provider_id)
        active_on = self.request.query_params.get("active_on")
        if active_on:
            active_date = parse_date(active_on)
            if active_date:
                qs = qs.filter(
                    Q(valid_from__isnull=True) | Q(valid_from__lte=active_date),
                    Q(valid_to__isnull=True) | Q(valid_to__gte=active_date),
                )
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "provider":
            raise PermissionDenied("Only providers can create availability slots.")

        provider = serializer.validated_data["provider"]
        if provider.user_id != user.id:
            raise PermissionDenied("You can only manage your own availability.")
        serializer.save()


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.select_related("client", "provider", "service").all()
    serializer_class = BookingSerializer
    permission_classes = [BookingRoleAccess]
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["start_time", "created_at", "status"]
    ordering = ["-start_time"]

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

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) != "client":
            raise PermissionDenied("Only clients can create bookings")

        try:
            booking = create_booking(
                client=self.request.user,
                provider=serializer.validated_data["provider"],
                service=serializer.validated_data["service"],
                start_time=serializer.validated_data["start_time"],
                end_time=serializer.validated_data.get("end_time"),
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        serializer.instance = booking

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        try:
            cancel_booking(booking=booking, actor=request.user)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return Response(self.get_serializer(booking).data)
