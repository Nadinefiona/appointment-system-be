import uuid

from django.db import models

from apps.providers.models import ServiceProvider


class ServiceType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    providers = models.ManyToManyField(
        ServiceProvider,
        related_name="service_types",
        blank=True,
    )

    def __str__(self):
        names = ", ".join(self.providers.values_list("user__username", flat=True)[:3])
        return f"{self.name} ({names or 'no providers'})"
