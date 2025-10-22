"""Payment models."""
from django.db import models

from tenants_core.core.models import TenantAwareModel


class Transaction(TenantAwareModel):
    """Transaction model."""

    booking_id = models.UUIDField(null=True, blank=True, db_index=True)
    customer_id = models.UUIDField(db_index=True)
    type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, db_index=True)
    method = models.CharField(max_length=50)
    provider = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payments_transaction"

    def __str__(self):
        return f"{self.type} - {self.amount}"
