from rest_framework import serializers

from .models import ServiceType


class ServiceTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = ServiceType
        fields = ["id", "provider", "name", "duration", "price"]
        read_only_fields = ["id"]
