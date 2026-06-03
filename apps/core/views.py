from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.serializers import MeProfileSerializer
from apps.core.openapi import ME_GET, ME_PATCH


@extend_schema_view(
    get=extend_schema(tags=["Account"], summary=ME_GET),
    patch=extend_schema(tags=["Account"], summary=ME_PATCH),
)
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user
