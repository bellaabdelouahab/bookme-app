"""
Tenant signals for lifecycle management.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Tenant, TenantLifecycle


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


@receiver(pre_delete, sender=Tenant)
def log_tenant_deletion(sender, instance, **kwargs):
    """Log tenant deletion event."""
    TenantLifecycle.objects.create(
        tenant=instance,
        event=TenantLifecycle.LifecycleEvent.DELETED,
        performed_by="system",
        metadata={"schema_name": instance.schema_name},
    )
