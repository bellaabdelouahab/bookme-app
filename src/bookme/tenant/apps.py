"""Tenant management app configuration."""
from django.apps import AppConfig


class TenantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookme.tenant"
    verbose_name = "Tenant Management"

    def ready(self):
        """Import signal handlers."""
        import bookme.tenant.signals  # noqa
