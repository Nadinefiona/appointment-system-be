from rest_framework import serializers

from .models import AvailabilitySlot, Booking


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def validate(self, attrs):
        if self.instance is not None and "provider" in attrs and attrs["provider"] != self.instance.provider:
            raise serializers.ValidationError({"provider": "Cannot move this slot to another provider."})
        return attrs

    class Meta:
        model = AvailabilitySlot
        fields = ["id", "provider", "weekday", "start_time", "end_time", "valid_from", "valid_to"]
        read_only_fields = ["id"]


class BookingSummarySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "start_time", "end_time", "status", "service", "client"]


class BookingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def validate(self, attrs):
        provider = attrs.get("provider")
        service = attrs.get("service")
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        if service and provider and service.provider_id != provider.id:
            raise serializers.ValidationError("Selected service does not belong to provider.")

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("end_time must be after start_time.")

        return attrs

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
        extra_kwargs = {"end_time": {"required": False}}
