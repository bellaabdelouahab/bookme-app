"""Booking models."""
from django.db import models

from bookme.core.models import TenantAwareModel


class Booking(TenantAwareModel):
    """Booking model."""

    customer_id = models.UUIDField(db_index=True)
    staff_id = models.UUIDField(db_index=True)
    service_id = models.UUIDField(db_index=True)
    booking_ref = models.CharField(max_length=50, unique=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50, db_index=True)
    channel = models.CharField(max_length=50)
    snapshot = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "bookings_booking"

    def __str__(self):
        return self.booking_ref


class BookingEvent(TenantAwareModel):
    """Booking event model."""

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50)
    actor = models.JSONField()
    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "bookings_event"

    def __str__(self):
        return f"{self.booking_id} - {self.event_type}"
