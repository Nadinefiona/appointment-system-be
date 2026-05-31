import uuid

from django.core.validators import MaxValueValidator
from django.db import models

from apps.accounts.models import User

from .buffer import MAX_BUFFER_MINUTES


class ServiceProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="provider_profile",
    )
    bio = models.TextField(blank=True)
    buffer_time = models.PositiveIntegerField(
        default=0,
        help_text="Buffer in minutes (max 480)",
        validators=[MaxValueValidator(MAX_BUFFER_MINUTES)],
    )

    def __str__(self):
        return self.user.get_username()
