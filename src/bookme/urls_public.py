"""
Public URL configuration (non-tenant routes).
"""
from django.conf import settings
from django.urls import include, path

from bookme.core.admin_site import public_admin_site
from bookme.tenant.views import TenantRegistrationView

urlpatterns = [
    # Public admin for super admins (manages tenants & shared apps)
    path("admin/", public_admin_site.urls),
    # Tenant registration/provisioning
    path("api/v1/tenants/register/", TenantRegistrationView.as_view(), name="tenant-register"),
    # Health check
    path("health/", lambda request: __import__("django.http").http.JsonResponse({"status": "ok"})),
]

# Titles are already set on public_admin_site in bookme.core.admin_site

# Debug toolbar (development only)
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
