"""
URL configuration for BookMe project (tenant-specific).
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API v1
    path("api/v1/auth/", include("tenants_core.users.urls")),
    path("api/v1/services/", include("base_start.services.urls")),
    path("api/v1/staff/", include("base_start.staff.urls")),
    path("api/v1/customers/", include("base_start.customers.urls")),
    path("api/v1/bookings/", include("base_start.bookings.urls")),
    path("api/v1/communications/", include("base_start.communications.urls")),
    path("api/v1/payments/", include("base_start.payments.urls")),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
