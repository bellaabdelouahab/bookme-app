"""Payments admin."""
from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "amount", "status", "method", "created_at"]
    list_filter = ["type", "status", "method"]
    search_fields = ["customer_id", "booking_id"]
