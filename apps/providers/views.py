from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import ServiceProvider
from .serializers import ServiceProviderSerializer


class ServiceProviderViewSet(ModelViewSet):
    queryset = ServiceProvider.objects.select_related('user').all()
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
