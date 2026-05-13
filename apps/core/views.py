from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from apps.accounts.serializers import UserSerializer
from apps.core.permissions import IsProvider
from apps.providers.models import ServiceProvider
from apps.providers.serializers import ProviderProfileSerializer


@extend_schema_view(
    get=extend_schema(
        tags=["Account"],
        summary="Current user",
        description="Returns the authenticated user (id, username, email, role, names).",
    )
)
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    get=extend_schema(
        tags=["Account"],
        summary="My provider profile",
        description="Returns **ServiceProvider** row for the logged-in provider (bio, buffer_time). 404 if not a provider.",
    ),
    patch=extend_schema(
        tags=["Account"],
        summary="Update my provider profile",
        description="Partial update of **bio** and **buffer_time** only. Providers cannot change their linked user here.",
    ),
)
class MeProviderProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProviderProfileSerializer
    permission_classes = [IsAuthenticated, IsProvider]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        user = self.request.user
        profile = ServiceProvider.objects.filter(user=user).first()
        if profile is None:
            raise NotFound("No provider profile exists for this account.")
        return profile
