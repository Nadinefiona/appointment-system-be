from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Obtain JWT (login)",
        description=(
            "Send `username` and `password` as JSON. "
            "Returns `access` and `refresh`. "
            "Use header `Authorization: Bearer <access>` on other endpoints."
        ),
    )
)
class SchemaTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Refresh JWT",
        description="Send `refresh` token to receive a new `access` token (and optionally a new `refresh`).",
    )
)
class SchemaTokenRefreshView(TokenRefreshView):
    pass
