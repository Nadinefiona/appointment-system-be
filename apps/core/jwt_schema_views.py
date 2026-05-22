from apps.accounts.jwt import EmailTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Obtain JWT (login)",
        description=(
            "Send `email` and `password` as JSON. "
            "Returns `access`, `refresh`, and `user` (id, email, **role**: `client`, `provider`, or `admin`). "
            "Use header `Authorization: Bearer <access>` on other endpoints."
        ),
    )
)
class SchemaTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Refresh JWT",
        description="Send `refresh` token to receive a new `access` token (and optionally a new `refresh`).",
    )
)
class SchemaTokenRefreshView(TokenRefreshView):
    pass
