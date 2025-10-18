"""Resources app configuration."""
from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookme.resources"
    verbose_name = "Resources"
