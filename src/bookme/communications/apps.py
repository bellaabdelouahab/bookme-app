"""Communications app configuration."""
from django.apps import AppConfig


class CommunicationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookme.communications"
    verbose_name = "Communications"
