from django.db import models

from apps.accounts.models import User


class ServiceProvider(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="provider_profile",
    )
    bio = models.TextField(blank=True)
    buffer_time = models.PositiveIntegerField(default=0, help_text="Buffer in minutes")

    def __str__(self):
        return self.user.get_username()
