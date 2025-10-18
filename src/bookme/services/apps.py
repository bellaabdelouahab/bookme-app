"""Services app configuration."""
from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookme.services"
    verbose_name = "Services"
