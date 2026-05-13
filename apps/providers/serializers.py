from rest_framework import serializers

from .models import ServiceProvider


class ServiceProviderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ["id", "user", "bio", "buffer_time"]
        read_only_fields = ["id"]


class ProviderProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ["id", "user", "bio", "buffer_time"]
        read_only_fields = ["id", "user"]
