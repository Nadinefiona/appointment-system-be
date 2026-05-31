from django.contrib import admin

from .models import ServiceType


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
    search_fields = ("name", "providers__user__username", "providers__user__email")
    filter_horizontal = ("providers",)
