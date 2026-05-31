from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.accounts.admin_views import AdminUserViewSet
from apps.accounts.views import RegisterView
from apps.bookings.views import AvailabilitySlotViewSet, BookingViewSet
from apps.core.views import MeView, health
from apps.providers.views import ServiceProviderViewSet
from apps.services.views import ServiceTypeViewSet

router = DefaultRouter()
router.register("providers", ServiceProviderViewSet, basename="provider")
router.register("services", ServiceTypeViewSet, basename="service")
router.register("availability-slots", AvailabilitySlotViewSet, basename="availability-slot")
router.register("bookings", BookingViewSet, basename="booking")
router.register("admin/users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
] + router.urls
