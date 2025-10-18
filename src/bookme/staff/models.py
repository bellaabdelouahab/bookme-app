"""Staff models."""
from django.db import models

from bookme.core.models import TenantAwareModel


class Staff(TenantAwareModel):
    """Staff model."""

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "staff_staff"

    def __str__(self):
        return self.full_name


class Availability(TenantAwareModel):
    """Staff availability model."""

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="availabilities")
    type = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    recurrence = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "staff_availability"

    def __str__(self):
        return f"{self.staff} - {self.type}"
