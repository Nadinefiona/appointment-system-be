from django.db import models

from apps.accounts.models import User
from apps.providers.models import ServiceProvider
from apps.services.models import ServiceType


class AvailabilitySlot(models.Model):
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name="availability_slots",
    )
    weekday = models.IntegerField(help_text="0=Monday, 6=Sunday")
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="availability_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.provider} - {self.weekday} {self.start_time}-{self.end_time}"


class Booking(models.Model):
    STATUS_BOOKED = "booked"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = (
        (STATUS_BOOKED, "Booked"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    service = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "start_time"],
                name="unique_booking_per_slot",
            ),
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="booking_end_after_start",
            ),
        ]
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.client.get_username()} -> {self.provider} ({self.start_time})"
