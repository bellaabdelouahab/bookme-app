"""
Tenant signals for lifecycle management and automation.
"""
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Domain, Tenant, TenantLifecycle


@receiver(post_save, sender=Tenant)
def log_tenant_creation(sender, instance, created, **kwargs):
    """Log tenant creation event."""
    if created:
        TenantLifecycle.objects.create(
            tenant=instance,
            event=TenantLifecycle.LifecycleEvent.CREATED,
            performed_by="system",
            metadata={"schema_name": instance.schema_name, "domain": instance.primary_domain},
        )

        # Auto-create primary Domain if configured and missing
        if getattr(settings, "TENANT_AUTO_CREATE_PRIMARY_DOMAIN", True):
            primary = instance.primary_domain

            # If admin set a bare subdomain (e.g., "acme"), expand using TENANT_BASE_DOMAIN
            if primary and "." not in primary:
                base = getattr(settings, "TENANT_BASE_DOMAIN", "localhost")
                primary = f"{primary}.{base}"

            if primary:
                # Persist any normalization back to tenant if needed
                if primary != instance.primary_domain:
                    Tenant.objects.filter(pk=instance.pk).update(primary_domain=primary)
                    instance.primary_domain = primary

                # Ensure a Domain exists and mark it primary
                Domain.objects.get_or_create(
                    domain=primary,
                    defaults={"tenant": instance, "is_primary": True},
                )


@receiver(pre_delete, sender=Tenant)
def log_tenant_deletion(sender, instance, **kwargs):
    """Log tenant deletion event."""
    TenantLifecycle.objects.create(
        tenant=None,  # Avoid FK issues during deletion; keep identifiers in metadata
        event=TenantLifecycle.LifecycleEvent.DELETED,
        performed_by="system",
        metadata={
            "tenant_id": getattr(instance, "id", None),
            "schema_name": instance.schema_name,
            "primary_domain": getattr(instance, "primary_domain", None),
        },
    )
