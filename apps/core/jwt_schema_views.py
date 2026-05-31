from apps.accounts.jwt import EmailTokenObtainPairSerializer
from apps.core.openapi import LOGIN, REFRESH
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema_view(
    post=extend_schema(tags=["Authentication"], summary=LOGIN),
)
class SchemaTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(tags=["Authentication"], summary=REFRESH),
)
class SchemaTokenRefreshView(TokenRefreshView):
    pass
