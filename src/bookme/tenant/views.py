"""
Tenant views for registration and management.
"""
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Domain, Tenant
from .serializers import TenantRegistrationSerializer


class TenantRegistrationView(APIView):
    """
    Public endpoint for tenant registration.
    Creates a new tenant with schema and domain.
    """

    permission_classes = []  # Public endpoint
    authentication_classes = []

    @transaction.atomic
    def post(self, request):
        """Create a new tenant."""
        serializer = TenantRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create tenant
        tenant_data = serializer.validated_data
        subdomain = tenant_data.pop("subdomain")

        tenant = Tenant.objects.create(
            name=tenant_data["name"],
            schema_name=f"tenant_{subdomain}",
            contact_email=tenant_data["contact_email"],
            contact_phone=tenant_data.get("contact_phone", ""),
            primary_domain=f"{subdomain}.bookme.ma",
        )

        # Create domain
        Domain.objects.create(
            domain=f"{subdomain}.bookme.ma",
            tenant=tenant,
            is_primary=True,
        )

        return Response(
            {
                "id": str(tenant.id),
                "name": tenant.name,
                "schema_name": tenant.schema_name,
                "domain": tenant.primary_domain,
                "status": tenant.status,
            },
            status=status.HTTP_201_CREATED,
        )
