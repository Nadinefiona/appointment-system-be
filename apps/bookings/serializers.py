from rest_framework import serializers

from .models import AvailabilitySlot, Booking


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = ["id", "provider", "weekday", "start_time", "end_time"]
        read_only_fields = ["id"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "client",
            "provider",
            "service",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "client", "created_at"]
