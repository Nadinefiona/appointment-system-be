from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import IsAdminOrAuthenticatedReadOnly

from .models import ServiceType
from .serializers import ServiceTypeSerializer


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
