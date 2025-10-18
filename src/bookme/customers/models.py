"""Customer models."""
from django.db import models

from bookme.core.models import TenantAwareModel


class Customer(TenantAwareModel):
    """Customer model."""

    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    locale = models.CharField(max_length=10, default="ar")
    consent = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "customers_customer"

    def __str__(self):
        return self.full_name
