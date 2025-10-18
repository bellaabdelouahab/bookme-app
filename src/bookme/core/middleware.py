"""
Middleware for tenant context and logging.
"""
import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant_model, schema_context

logger = logging.getLogger(__name__)


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
