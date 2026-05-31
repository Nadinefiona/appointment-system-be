from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.openapi import REGISTER

from .serializers import RegisterSerializer


@extend_schema_view(
    post=extend_schema(tags=["Registration"], summary=REGISTER),
)
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "message": "Registration successful. Obtain a token at POST /api/token/ using your email and password.",
            },
            status=status.HTTP_201_CREATED,
        )
