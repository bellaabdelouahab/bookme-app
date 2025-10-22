"""Bookings app configuration."""
from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "base_start.bookings"
    verbose_name = "Bookings"
