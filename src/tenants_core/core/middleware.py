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
    """
    Ensure only members of the current tenant (or superusers) can access tenant admin.

    This middleware:
    1. Blocks non-members from accessing /admin/
    2. Adds request.user_role property with the user's TenantRole
    3. Adds request.user_membership property with the TenantMembership
    4. Checks RBAC permissions via TenantRole system
    """

    def process_request(self, request):
        path = request.path or ""
        user = getattr(request, "user", None)
        tenant = getattr(request, "current_tenant", None)

        # Initialize user_role and user_membership attributes
        request.user_role = None
        request.user_membership = None

        # Only process admin paths
        if not path.startswith("/admin"):
            return None

        # Allow anonymous to reach login page
        if not user or not user.is_authenticated:
            return None

        # Superusers can always access
        if getattr(user, "is_superuser", False):
            return None

        # On public schema, only allow superusers and platform staff
        schema_name = getattr(tenant, "schema_name", None)
        if schema_name in (None, "public"):
            # Check if user has platform admin access
            if user.is_superuser or getattr(user, 'is_platform_staff', False):
                return None
            # Block regular users from accessing platform admin
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(
                "You do not have platform admin access. "
                "This admin interface is for platform administrators only. "
                "To access your tenant admin, visit: http://&lt;your-tenant&gt;.localhost:8000/admin/"
            )

        # Check membership and get role
        try:
            from tenants_core.users.models import TenantMembership
        except Exception:
            return None

        try:
            membership = TenantMembership.objects.select_related('tenant_role').get(
                user=user,
                tenant_id=getattr(tenant, "id", None),
                is_active=True
            )

            # Add membership and role to request for easy access in views
            request.user_membership = membership
            request.user_role = membership.tenant_role

            # Optionally log the user's role for debugging
            if membership.tenant_role:
                logger.debug(
                    f"User {user.email} accessing admin with role: {membership.tenant_role.name}"
                )

            # Access granted - user is a member with a role
            return None

        except TenantMembership.DoesNotExist:
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden(
                "You are not a member of this tenant. Ask an owner/admin to add you."
            )

        return None
