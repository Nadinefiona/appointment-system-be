from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.viewsets import ModelViewSet

from .models import AvailabilitySlot, Booking
from .serializers import AvailabilitySlotSerializer, BookingSerializer
from .services import create_booking
from apps.core.permissions import AvailabilitySlotAccess, BookingRoleAccess


class AvailabilitySlotViewSet(ModelViewSet):
    queryset = AvailabilitySlot.objects.select_related("provider", "provider__user").all()
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [AvailabilitySlotAccess]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            return self.queryset
        if getattr(user, "role", None) == "provider":
            return self.queryset.filter(provider__user=user)
        return self.queryset.none()

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

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "admin":
            return self.queryset
        if role == "provider":
            return self.queryset.filter(provider__user=user)
        return self.queryset.filter(client=user)

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) != "client":
            raise PermissionDenied("Only clients can create bookings")

        try:
            booking = create_booking(
                client=self.request.user,
                provider=serializer.validated_data["provider"],
                service=serializer.validated_data["service"],
                start_time=serializer.validated_data["start_time"],
                end_time=serializer.validated_data["end_time"],
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        serializer.instance = booking
