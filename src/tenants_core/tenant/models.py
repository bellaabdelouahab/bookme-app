"""
Tenant models for multi-tenant schema isolation.
"""
import uuid

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    """
    Tenant model representing a single business/organization.
    Each tenant gets its own PostgreSQL schema.
    """

    # Override auto-increment ID with UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class TenantStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        TRIAL = "trial", "Trial"
        CANCELLED = "cancelled", "Cancelled"

    class AppType(models.TextChoices):
        SALON = "salon", "Salon / Barbershop"
        CLINIC = "clinic", "Medical Clinic"
        GYM = "gym", "Gym / Fitness Center"
        SPA = "spa", "Spa / Wellness Center"
        STUDIO = "studio", "Studio (Yoga, Dance, Art)"
        RESTAURANT = "restaurant", "Restaurant"
        CUSTOM = "custom", "Custom / Other"

    name = models.CharField(max_length=255, help_text="Business/Company name")
    status = models.CharField(
        max_length=20,
        choices=TenantStatus.choices,
        default=TenantStatus.TRIAL,
        db_index=True,
    )
    app_type = models.CharField(
        max_length=20,
        choices=AppType.choices,
        default=AppType.CUSTOM,
        db_index=True,
        help_text="Type of business - determines which modules are enabled",
    )
    primary_domain = models.CharField(max_length=255, unique=True)

    # Contact information
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)

    # Subscription & limits
    subscription_tier = models.CharField(max_length=50, default="free")
    max_staff = models.PositiveIntegerField(default=5)
    max_services = models.PositiveIntegerField(default=10)
    max_bookings_per_month = models.PositiveIntegerField(default=100)

    # Module configuration
    enabled_modules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Granular control over enabled modules from base_start (e.g., {'bookings': True, 'payments': False})",
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # django-tenants required fields (inherited from TenantMixin)
    # - schema_name
    # - auto_create_schema
    # - auto_drop_schema

    class Meta:
        db_table = "tenant_tenant"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["subscription_tier"]),
            models.Index(fields=["app_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.schema_name})"

    @property
    def is_active(self):
        """Check if tenant is active."""
        return self.status == self.TenantStatus.ACTIVE

    def save(self, *args, **kwargs):
        """Ensure schema_name present; views/admin should set it explicitly."""
        if not self.schema_name and self.primary_domain:
            # Derive from primary_domain if missing (fallback)
            slug = self.primary_domain.split(".")[0].lower()
            self.schema_name = f"tenant_{slug}"
        super().save(*args, **kwargs)


class Domain(DomainMixin):
    """
    Domain model for tenant routing.
    Maps domains/subdomains to tenants.
    """

    class Meta:
        db_table = "tenant_domain"

    def __str__(self):
        return f"{self.domain} -> {self.tenant}"


class TenantConfig(models.Model):
    """
    Flexible key-value configuration store for tenant settings.
    Allows extending tenant configuration without schema changes.
    """

    class ConfigCategory(models.TextChoices):
        BRANDING = "branding", "Branding"
        LOCALE = "locale", "Localization"
        FEATURES = "features", "Features"
        LIMITS = "limits", "Limits"
        INTEGRATIONS = "integrations", "Integrations"
        NOTIFICATIONS = "notifications", "Notifications"
        PAYMENTS = "payments", "Payments"
        CUSTOM = "custom", "Custom"

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="configs",
    )
    category = models.CharField(
        max_length=50,
        choices=ConfigCategory.choices,
        default=ConfigCategory.CUSTOM,
        db_index=True,
    )
    key = models.CharField(max_length=255)
    value = models.JSONField()
    is_encrypted = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenant_config"
        unique_together = [["tenant", "category", "key"]]
        ordering = ["category", "key"]
        indexes = [
            models.Index(fields=["tenant", "category"]),
            models.Index(fields=["key"]),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.category}:{self.key}"


class TenantLifecycle(models.Model):
    """
    Audit log for tenant lifecycle events.
    Tracks creation, subscription changes, suspension, etc.
    """

    class LifecycleEvent(models.TextChoices):
        CREATED = "created", "Created"
        ACTIVATED = "activated", "Activated"
        SUSPENDED = "suspended", "Suspended"
        REACTIVATED = "reactivated", "Reactivated"
        UPGRADED = "upgraded", "Upgraded"
        DOWNGRADED = "downgraded", "Downgraded"
        CANCELLED = "cancelled", "Cancelled"
        DELETED = "deleted", "Deleted"

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lifecycle_events",
    )
    event = models.CharField(max_length=50, choices=LifecycleEvent.choices, db_index=True)
    performed_by = models.CharField(max_length=255, blank=True)  # User ID or "system"
    metadata = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenant_lifecycle"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["tenant", "event"]),
            models.Index(fields=["occurred_at"]),
        ]

    def __str__(self):
        if self.tenant is not None:
            tenant_label = self.tenant.name
        else:
            # Fallback to metadata captured at deletion time
            md = self.metadata or {}
            tenant_label = md.get("primary_domain") or md.get("schema_name") or f"tenant:{md.get('tenant_id', '?')}"
        return f"{tenant_label} - {self.event} at {self.occurred_at}"
