"""
Custom exception handlers.
"""
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Customize the response format
        error_data = {"error": {"message": str(exc), "code": response.status_code, "details": None}}

        if hasattr(exc, "detail"):
            error_data["error"]["details"] = exc.detail

        response.data = error_data
        return response

    # Handle Django exceptions
    if isinstance(exc, Http404):
        return Response(
            {"error": {"message": "Not found.", "code": 404, "details": str(exc)}},
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {"error": {"message": "Permission denied.", "code": 403, "details": str(exc)}},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Log unhandled exceptions
    logger.exception("Unhandled exception", exc_info=exc)

    return Response(
        {
            "error": {
                "message": "An unexpected error occurred.",
                "code": 500,
                "details": str(exc) if settings.DEBUG else None,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class TenantLimitExceeded(APIException):
    """Exception raised when tenant exceeds their subscription limits."""

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = "Tenant has exceeded their subscription limits."
    default_code = "tenant_limit_exceeded"


class TenantInactive(APIException):
    """Exception raised when tenant is inactive or suspended."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Tenant account is inactive or suspended."
    default_code = "tenant_inactive"
