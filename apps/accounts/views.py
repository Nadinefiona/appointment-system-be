from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import RegisterProviderSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Registration"],
        summary="Register as provider",
        description=(
            "Creates a **provider** user and linked **ServiceProvider** profile. "
            "No authentication required. Then call **Authentication** / Obtain JWT with the same username/password."
        ),
    )
)
class ProviderRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterProviderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "message": "Registration successful. Obtain a token at POST /api/token/ using your username and password.",
            },
            status=status.HTTP_201_CREATED,
        )
