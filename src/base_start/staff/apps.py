"""Staff app configuration."""
from django.apps import AppConfig


class StaffConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "base_start.staff"
    verbose_name = "Staff"
