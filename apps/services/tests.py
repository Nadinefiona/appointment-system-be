from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import ServiceProvider
from apps.services.models import ServiceType

User = get_user_model()


class ServiceProvidersApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass",
            role=User.ROLE_ADMIN,
        )
        self.provider_a = ServiceProvider.objects.create(
            user=User.objects.create_user(
                username="pa",
                email="pa@example.com",
                password="pass",
                role=User.ROLE_PROVIDER,
                first_name="Alice",
                last_name="One",
            )
        )
        self.provider_b = ServiceProvider.objects.create(
            user=User.objects.create_user(
                username="pb",
                email="pb@example.com",
                password="pass",
                role=User.ROLE_PROVIDER,
                first_name="Bob",
                last_name="Two",
            )
        )
        self.api.force_authenticate(user=self.admin)

    def test_create_service_with_multiple_providers(self):
        response = self.api.post(
            "/api/services/",
            {
                "name": "BBL",
                "providers": [str(self.provider_a.pk), str(self.provider_b.pk)],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["provider_details"]), 2)
        self.assertEqual(response.data["provider_details"][0]["first_name"], "Alice")

    def test_rejects_duplicate_provider_on_service(self):
        pid = str(self.provider_a.pk)
        response = self.api.post(
            "/api/services/",
            {"name": "Dup", "providers": [pid, pid]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
