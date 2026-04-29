from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import AvailabilitySlot, Booking
from .serializers import AvailabilitySlotSerializer, BookingSerializer
from .services import create_booking


class AvailabilitySlotViewSet(ModelViewSet):
    queryset = AvailabilitySlot.objects.select_related('provider', 'provider__user').all()
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.select_related('client', 'provider', 'service').all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        if user.role == 'provider':
            return self.queryset.filter(provider__user=user)
        return self.queryset.filter(client=user)

    def perform_create(self, serializer):
        booking = create_booking(
            client=self.request.user,
            provider=serializer.validated_data['provider'],
            service=serializer.validated_data['service'],
            start_time=serializer.validated_data['start_time'],
            end_time=serializer.validated_data['end_time'],
        )
        serializer.instance = booking
