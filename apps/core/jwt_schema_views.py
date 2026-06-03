from apps.accounts.jwt import EmailTokenObtainPairSerializer
from apps.core.openapi import LOGIN
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView


@extend_schema_view(
    post=extend_schema(tags=["Authentication"], summary=LOGIN, auth=[]),
)
class SchemaTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    serializer_class = EmailTokenObtainPairSerializer
