from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import ServiceProvider

User = get_user_model()


class RegisterAndLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_client(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "client@example.com",
                "password": "securepass123",
                "password_confirm": "securepass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], User.ROLE_CLIENT)
        user = User.objects.get(email="client@example.com")
        self.assertEqual(user.role, User.ROLE_CLIENT)
        self.assertFalse(ServiceProvider.objects.filter(user=user).exists())

    def test_login_with_email_and_password(self):
        User.objects.create_user(
            username="client",
            email="login@example.com",
            password="securepass123",
            role=User.ROLE_CLIENT,
        )
        response = self.client.post(
            "/api/token/",
            {"email": "login@example.com", "password": "securepass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], User.ROLE_CLIENT)
        self.assertEqual(response.data["user"]["email"], "login@example.com")

    def test_login_rejects_username_field(self):
        User.objects.create_user(
            username="onlyuser",
            email="user@example.com",
            password="securepass123",
        )
        response = self.client.post(
            "/api/token/",
            {"username": "onlyuser", "password": "securepass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
