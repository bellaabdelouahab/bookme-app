"""
Public URL configuration (non-tenant routes).
"""
from django.urls import path

from bookme.tenant.views import TenantRegistrationView

urlpatterns = [
    # Tenant registration/provisioning
    path("api/v1/tenants/register/", TenantRegistrationView.as_view(), name="tenant-register"),
    # Health check
    path("health/", lambda request: __import__("django.http").http.JsonResponse({"status": "ok"})),
]
