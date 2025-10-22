"""RBAC app configuration."""
from django.apps import AppConfig


class RbacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants_core.rbac"
    verbose_name = "Role-Based Access Control"

    def ready(self):
        """Import signals when app is ready."""
        import tenants_core.rbac.signals  # noqa: F401
