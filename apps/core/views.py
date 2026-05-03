from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.serializers import UserSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
