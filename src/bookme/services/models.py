"""Service models."""
from django.db import models

from bookme.core.models import TenantAwareModel


class Service(TenantAwareModel):
    """Service catalog model."""

    name = models.JSONField(help_text="Localized service name")
    description = models.JSONField(help_text="Localized service description")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "services_service"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)
