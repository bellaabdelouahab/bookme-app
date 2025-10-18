"""Resource models."""
from django.db import models

from bookme.core.models import TenantAwareModel


class Resource(TenantAwareModel):
    """Generic resource model."""

    resource_type = models.CharField(max_length=50, db_index=True)
    key = models.CharField(max_length=255)
    content = models.JSONField()
    locale = models.CharField(max_length=10, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "resources_resource"

    def __str__(self):
        return f"{self.resource_type} - {self.key}"
