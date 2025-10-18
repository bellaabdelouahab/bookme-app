"""Staff admin."""
from django.contrib import admin

from .models import Availability, Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["full_name", "email"]


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["staff", "type", "start_time", "end_time"]
    list_filter = ["type"]
