from rest_framework import serializers

from apps.providers.models import ServiceProvider

from .models import ServiceType


class ServiceProviderBriefSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ["id", "first_name", "last_name", "email"]


class ServiceTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    providers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceProvider.objects.select_related("user").all(),
    )
    provider_details = ServiceProviderBriefSerializer(
        source="providers",
        many=True,
        read_only=True,
    )

    class Meta:
        model = ServiceType
        fields = ["id", "name", "providers", "provider_details"]
        read_only_fields = ["id", "provider_details"]

    def validate_providers(self, providers):
        ids = [p.pk for p in providers]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Each provider can only be added once per service.")
        return providers

    def create(self, validated_data):
        providers = validated_data.pop("providers", [])
        service = ServiceType.objects.create(**validated_data)
        service.providers.set(providers)
        return service

    def update(self, instance, validated_data):
        providers = validated_data.pop("providers", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if providers is not None:
            instance.providers.set(providers)
        return instance
