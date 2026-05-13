from django.contrib import admin

from .models import AvailabilitySlot, Booking


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("provider", "weekday", "start_time", "end_time", "valid_from", "valid_to", "id")
    list_filter = ("weekday", "provider")
    search_fields = ("provider__user__username", "provider__user__email")
    raw_id_fields = ("provider",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "status", "client", "provider", "service", "id")
    list_filter = ("status", "provider")
    search_fields = ("client__email", "client__username", "provider__user__username")
    raw_id_fields = ("client", "provider", "service")
    date_hierarchy = "start_time"
