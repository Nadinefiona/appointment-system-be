from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import ServiceType
from .serializers import ServiceTypeSerializer


class ServiceTypeViewSet(ModelViewSet):
    queryset = ServiceType.objects.select_related('provider', 'provider__user').all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated]
