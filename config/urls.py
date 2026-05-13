from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.jwt_schema_views import SchemaTokenObtainPairView, SchemaTokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    path("api/token/", SchemaTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", SchemaTokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("apps.core.api_urls")),
]
