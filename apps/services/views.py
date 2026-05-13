from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import IsAdminOrAuthenticatedReadOnly

from .models import ServiceType
from .serializers import ServiceTypeSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Services"],
        summary="List services",
        description="Catalog of **ServiceType** rows. Filter with `?provider=<uuid>`. Authenticated read; admin writes.",
    ),
    retrieve=extend_schema(tags=["Services"], summary="Get service"),
    create=extend_schema(tags=["Services"], summary="Create service (admin)"),
    update=extend_schema(tags=["Services"], summary="Replace service (admin)"),
    partial_update=extend_schema(tags=["Services"], summary="Patch service (admin)"),
    destroy=extend_schema(tags=["Services"], summary="Delete service (admin)"),
)
class ServiceTypeViewSet(ModelViewSet):
    queryset = ServiceType.objects.select_related("provider", "provider__user").all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAuthenticatedReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "price", "duration"]
    ordering = ["name"]

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        provider_id = self.request.query_params.get("provider")
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        return qs
