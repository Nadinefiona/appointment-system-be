from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_PROVIDER = "provider"
    ROLE_CLIENT = "client"

    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_PROVIDER, "Provider"),
        (ROLE_CLIENT, "Client"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CLIENT)
