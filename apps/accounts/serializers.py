from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.providers.models import ServiceProvider

from apps.providers.buffer import MAX_BUFFER_MINUTES

from .models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]
        read_only_fields = ["id"]


class ProviderProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ["id", "bio", "buffer_time"]
        read_only_fields = ["id"]

    def validate_buffer_time(self, value):
        if value > MAX_BUFFER_MINUTES:
            raise serializers.ValidationError(
                f"Buffer time cannot exceed {MAX_BUFFER_MINUTES} minutes (8 hours)."
            )
        return value


class MeProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    role = serializers.CharField(read_only=True)
    provider_profile = ProviderProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "provider_profile"]
        read_only_fields = ["id", "username", "role"]

    def validate_email(self, value):
        value = value.strip().lower()
        user = self.instance
        qs = User.objects.filter(email__iexact=value)
        if user:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = ServiceProvider.objects.filter(user=instance).first()
        data["provider_profile"] = (
            ProviderProfileSerializer(profile).data if profile else None
        )
        return data

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("provider_profile", None)
        instance = super().update(instance, validated_data)
        if profile_data is None:
            return instance
        if instance.role != User.ROLE_PROVIDER:
            raise serializers.ValidationError(
                {"provider_profile": "Only provider accounts have a provider profile."}
            )
        profile, _ = ServiceProvider.objects.get_or_create(user=instance)
        profile_serializer = ProviderProfileSerializer(profile, data=profile_data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        return instance


class AdminUserListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "role"]
        read_only_fields = fields


class AdminUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role"]


def username_from_email(email: str) -> str:
    """Derive a unique username from an email address."""
    base = email.split("@", 1)[0][:150] or "user"
    candidate = base
    suffix = 1
    while User.objects.filter(username__iexact=candidate).exists():
        tail = f"_{suffix}"
        candidate = f"{base[: 150 - len(tail)]}{tail}"
        suffix += 1
    return candidate


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        email = validated_data["email"]
        user = User.objects.create_user(
            username=username_from_email(email),
            email=email,
            password=password,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=User.ROLE_CLIENT,
        )
        return user
