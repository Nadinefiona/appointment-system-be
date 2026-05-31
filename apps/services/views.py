from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.openapi import (
    SERVICES_CREATE,
    SERVICES_DELETE,
    SERVICES_GET,
    SERVICES_LIST,
    SERVICES_PATCH,
    SERVICES_UPDATE,
)
from apps.core.permissions import IsAdminOrAuthenticatedReadOnly

from .models import ServiceType
from .serializers import ServiceTypeSerializer


@extend_schema_view(
    list=extend_schema(tags=["Services"], summary=SERVICES_LIST),
    retrieve=extend_schema(tags=["Services"], summary=SERVICES_GET),
    create=extend_schema(tags=["Services"], summary=SERVICES_CREATE),
    update=extend_schema(tags=["Services"], summary=SERVICES_UPDATE),
    partial_update=extend_schema(tags=["Services"], summary=SERVICES_PATCH),
    destroy=extend_schema(tags=["Services"], summary=SERVICES_DELETE),
)
class ServiceTypeViewSet(ModelViewSet):
    queryset = ServiceType.objects.prefetch_related("providers", "providers__user").all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAuthenticatedReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        provider_id = self.request.query_params.get("provider")
        if provider_id:
            qs = qs.filter(providers__id=provider_id).distinct()
        return qs
