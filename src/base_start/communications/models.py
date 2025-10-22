"""Communication models."""
from django.db import models

from tenants_core.core.models import TenantAwareModel


class NotificationTemplate(TenantAwareModel):
    """Notification template model."""

    name = models.CharField(max_length=255)
    channel = models.CharField(max_length=50)
    content = models.JSONField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "communications_template"

    def __str__(self):
        return self.name


class Notification(TenantAwareModel):
    """Notification model."""

    recipient_type = models.CharField(max_length=50)
    recipient_id = models.UUIDField(db_index=True)
    channel = models.CharField(max_length=50)
    template_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=50, db_index=True)
    payload = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "communications_notification"

    def __str__(self):
        return f"{self.recipient_type} - {self.channel}"
