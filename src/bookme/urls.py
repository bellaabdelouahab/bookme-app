"""
URL configuration for BookMe project (tenant-specific).
"""
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
    path("api/v1/auth/", include("bookme.users.urls")),
    path("api/v1/services/", include("bookme.services.urls")),
    path("api/v1/staff/", include("bookme.staff.urls")),
    path("api/v1/customers/", include("bookme.customers.urls")),
    path("api/v1/bookings/", include("bookme.bookings.urls")),
    path("api/v1/communications/", include("bookme.communications.urls")),
    path("api/v1/payments/", include("bookme.payments.urls")),
]
