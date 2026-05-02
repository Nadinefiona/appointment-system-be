from rest_framework import serializers

from .models import ServiceProvider


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ["id", "user", "bio", "buffer_time"]
        read_only_fields = ["id"]
