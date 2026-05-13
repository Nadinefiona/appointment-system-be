from django.contrib import admin

from .models import ServiceType


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "duration", "price", "id")
    list_filter = ("provider",)
    search_fields = ("name", "provider__user__username")
    raw_id_fields = ("provider",)
