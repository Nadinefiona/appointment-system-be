from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import ProviderRegisterView
from apps.bookings.views import AvailabilitySlotViewSet, BookingViewSet
from apps.core.views import MeProviderProfileView, MeView
from apps.providers.views import ServiceProviderViewSet
from apps.services.views import ServiceTypeViewSet

router = DefaultRouter()
router.register("providers", ServiceProviderViewSet, basename="provider")
router.register("services", ServiceTypeViewSet, basename="service")
router.register("availability-slots", AvailabilitySlotViewSet, basename="availability-slot")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("auth/register/provider/", ProviderRegisterView.as_view(), name="register-provider"),
    path("me/", MeView.as_view(), name="me"),
    path("me/provider-profile/", MeProviderProfileView.as_view(), name="me-provider-profile"),
] + router.urls
