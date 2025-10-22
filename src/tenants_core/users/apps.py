"""Users app configuration."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants_core.users"
    verbose_name = "Users & Authentication"

    def ready(self):
        # Register user signals
        import tenants_core.users.signals  # noqa: F401
