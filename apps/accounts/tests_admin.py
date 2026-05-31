from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import ServiceProvider

User = get_user_model()


class AdminUserApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass",
            role=User.ROLE_ADMIN,
        )
        self.client_user = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="pass",
            role=User.ROLE_CLIENT,
        )
        self.api.force_authenticate(user=self.admin)

    def test_list_users(self):
        response = self.api.get("/api/admin/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        emails = [u["email"] for u in response.data]
        self.assertIn("client@example.com", emails)

    def test_patch_role_to_provider(self):
        response = self.api.patch(
            f"/api/admin/users/{self.client_user.pk}/",
            {"role": User.ROLE_PROVIDER},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], User.ROLE_PROVIDER)
        self.client_user.refresh_from_db()
        self.assertTrue(ServiceProvider.objects.filter(user=self.client_user).exists())

    def test_cannot_patch_email(self):
        response = self.api.patch(
            f"/api/admin/users/{self.client_user.pk}/",
            {"role": User.ROLE_CLIENT, "email": "hacked@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.email, "client@example.com")
