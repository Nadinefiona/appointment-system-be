from django.contrib import admin

from .models import ServiceProvider


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "buffer_time", "id")
    list_select_related = ("user",)
    search_fields = ("user__username", "user__email", "bio")
    raw_id_fields = ("user",)
