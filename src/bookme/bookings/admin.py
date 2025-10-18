"""Booking admin."""
from django.contrib import admin

from .models import Booking, BookingEvent


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["booking_ref", "customer_id", "staff_id", "start_time", "status", "created_at"]
    list_filter = ["status", "channel"]
    search_fields = ["booking_ref", "customer_id", "staff_id"]


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = ["booking", "event_type", "created_at"]
    list_filter = ["event_type"]
