"""
Middleware for host validation, tenant context, and logging.
"""
import logging
import time
import uuid

from django.core.exceptions import DisallowedHost
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import schema_context  # noqa: F401  # may be used in future

from .host_validation import get_allowed_hosts_dynamic, host_matches_base_wildcard

logger = logging.getLogger(__name__)


class DynamicAllowedHostsMiddleware(MiddlewareMixin):
    """Allow hosts that exist in DB Domains or match base wildcard.

    This reduces the need to constantly update ALLOWED_HOSTS when adding tenants.
    It runs before tenant routing.
    """

    def process_request(self, request):
        host = request.get_host().split(":")[0].lower()

        # Always allow localhost shortcuts
        if host in {"localhost", "127.0.0.1"}:
            return None

        # Allow if in configured hosts or in DB domains
        dynamic_hosts = get_allowed_hosts_dynamic()
        if host in dynamic_hosts or host_matches_base_wildcard(host):
            return None

        raise DisallowedHost(host)


class TenantContextMiddleware(MiddlewareMixin):
    """
    Middleware to add tenant context to all requests.
    Provides easy access to current tenant.
    """

    def process_request(self, request):
        """Add tenant to request object."""
        try:
            # Get tenant from django-tenants
            tenant = request.tenant if hasattr(request, "tenant") else None
            request.current_tenant = tenant
        except Exception as e:
            logger.error(f"Error getting tenant context: {e}")
            request.current_tenant = None


class StructuredLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to add structured logging context to all requests.
    """

    def process_request(self, request):
        """Add request context."""
        request.request_id = str(uuid.uuid4())
        request.start_time = time.time()

    def process_response(self, request, response):
        """Log request completion."""
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            tenant_name = getattr(request.current_tenant, "name", "N/A") if hasattr(
                request, "current_tenant"
            ) else "N/A"

            logger.info(
                "Request completed",
                extra={
                    "request_id": getattr(request, "request_id", "N/A"),
                    "tenant": tenant_name,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "user": str(request.user) if hasattr(request, "user") else "Anonymous",
                },
            )

        return response


class TenantAdminAccessMiddleware(MiddlewareMixin):
    """Ensure only members of the current tenant (or superusers) can access tenant admin.

    This does not grant Django model permissions; it just blocks access to /admin/
    for non-members to avoid confusion and tighten security.
    """

    def process_request(self, request):
        path = request.path or ""
        if not path.startswith("/admin"):
            return None

        user = getattr(request, "user", None)
        tenant = getattr(request, "current_tenant", None)

        # Allow anonymous to reach login page
        if not user or not user.is_authenticated:
            return None

        # Superusers can always access
        if getattr(user, "is_superuser", False):
            return None

        # On public schema, fall back to default admin behavior
        schema_name = getattr(tenant, "schema_name", None)
        if schema_name in (None, "public"):
            return None

        # Check membership
        try:
            from bookme.users.models import TenantMembership
        except Exception:
            return None

        is_member = TenantMembership.objects.filter(
            user=user, tenant_id=getattr(tenant, "id", None), is_active=True
        ).exists()

        if not is_member:
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden(
                "You are not a member of this tenant. Ask an owner/admin to add you."
            )

        return None
