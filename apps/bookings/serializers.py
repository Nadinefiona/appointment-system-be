from rest_framework import serializers

from apps.accounts.models import User
from apps.providers.models import ServiceProvider
from apps.services.models import ServiceType

from .models import AvailabilitySlot, Booking


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    provider = serializers.UUIDField(source="provider_id", read_only=True)

    class Meta:
        model = AvailabilitySlot
        fields = ["id", "provider", "weekday", "start_time", "end_time"]
        read_only_fields = ["id", "provider"]

    @staticmethod
    def _times_overlap(start_a, end_a, start_b, end_b):
        return start_a < end_b and end_a > start_b

    def validate(self, attrs):
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("end_time must be after start_time.")
        weekday = attrs.get("weekday", getattr(self.instance, "weekday", None))
        if weekday is not None and weekday not in range(7):
            raise serializers.ValidationError({"weekday": "Must be 0 (Monday) through 6 (Sunday)."})

        provider = self.context.get("provider")
        if provider is None and self.instance is not None:
            provider = self.instance.provider

        if provider is not None and weekday is not None and start_time and end_time:
            others = AvailabilitySlot.objects.filter(provider=provider, weekday=weekday)
            if self.instance is not None:
                others = others.exclude(pk=self.instance.pk)
            for slot in others:
                if self._times_overlap(start_time, end_time, slot.start_time, slot.end_time):
                    raise serializers.ValidationError(
                        "This time overlaps another slot on the same day. "
                        "Edit or delete the existing slot first."
                    )
        return attrs


class BookingServiceBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["id", "name"]


class BookingProviderBriefSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ["id", "first_name", "last_name", "email"]


class BookingClientBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class BookingSummarySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    service = BookingServiceBriefSerializer(read_only=True)
    provider = BookingProviderBriefSerializer(read_only=True)
    client = BookingClientBriefSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "start_time",
            "end_time",
            "status",
            "service",
            "provider",
            "client",
            "note",
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=2000)

    def validate(self, attrs):
        provider = attrs.get("provider")
        service = attrs.get("service")
        if service and provider and not service.providers.filter(pk=provider.pk).exists():
            raise serializers.ValidationError("Selected provider does not offer this service.")
        return attrs

    class Meta:
        model = Booking
        fields = ["provider", "service", "start_time", "note"]


class BookingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    service = BookingServiceBriefSerializer(read_only=True)
    provider = BookingProviderBriefSerializer(read_only=True)
    client = BookingClientBriefSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "client",
            "provider",
            "service",
            "start_time",
            "end_time",
            "note",
            "status",
            "created_at",
        ]
        read_only_fields = fields
