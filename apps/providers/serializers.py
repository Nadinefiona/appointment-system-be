from rest_framework import serializers

from apps.providers.buffer import MAX_BUFFER_MINUTES

from .models import ServiceProvider


class ServiceProviderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.UUIDField(source="user_id", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ServiceProvider
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "email",
            "bio",
            "buffer_time",
        ]
        read_only_fields = ["id", "user", "first_name", "last_name", "email"]

    def validate_buffer_time(self, value):
        if value > MAX_BUFFER_MINUTES:
            raise serializers.ValidationError(
                f"Buffer time cannot exceed {MAX_BUFFER_MINUTES} minutes (8 hours)."
            )
        return value
