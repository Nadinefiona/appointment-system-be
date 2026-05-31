from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.openapi import ADMIN_USER_LIST, ADMIN_USER_ROLE
from apps.core.permissions import IsAdmin
from apps.providers.models import ServiceProvider

from .models import User
from .serializers import AdminUserListSerializer, AdminUserRoleSerializer


@extend_schema_view(
    list=extend_schema(tags=["Admin"], summary=ADMIN_USER_LIST),
    partial_update=extend_schema(tags=["Admin"], summary=ADMIN_USER_ROLE),
)
class AdminUserViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all().order_by("email")
    http_method_names = ["get", "patch", "head", "options"]
    lookup_field = "pk"
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return AdminUserRoleSerializer
        return AdminUserListSerializer

    def perform_update(self, serializer):
        user = serializer.save()
        if user.role == User.ROLE_PROVIDER:
            ServiceProvider.objects.get_or_create(user=user)
