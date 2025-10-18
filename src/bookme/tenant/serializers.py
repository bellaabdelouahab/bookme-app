"""
Tenant serializers for API endpoints.
"""
from rest_framework import serializers

from .models import Tenant


class TenantRegistrationSerializer(serializers.Serializer):
    """Serializer for tenant registration."""

    name = serializers.CharField(max_length=255)
    subdomain = serializers.SlugField(max_length=63)
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_subdomain(self, value):
        """Validate subdomain uniqueness and format."""
        # Check if subdomain already exists
        if Tenant.objects.filter(schema_name=f"tenant_{value}").exists():
            raise serializers.ValidationError("This subdomain is already taken.")

        # Reserved subdomains
        reserved = ["www", "api", "admin", "app", "mail", "ftp", "localhost", "staging"]
        if value.lower() in reserved:
            raise serializers.ValidationError("This subdomain is reserved.")

        return value.lower()


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for tenant details."""

    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "schema_name",
            "primary_domain",
            "status",
            "subscription_tier",
            "contact_email",
            "contact_phone",
            "max_staff",
            "max_services",
            "max_bookings_per_month",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "schema_name", "created_at", "updated_at"]
