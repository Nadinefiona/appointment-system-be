from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.providers.models import ServiceProvider

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Role",
            {
                "fields": ("role",),
                "description": (
                    "New sign-ups are clients. Set role to Provider here to grant provider access; "
                    "a ServiceProvider profile is created automatically."
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.role == User.ROLE_PROVIDER:
            ServiceProvider.objects.get_or_create(user=obj)
