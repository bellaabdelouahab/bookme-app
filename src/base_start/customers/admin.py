"""Customer admin."""
from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "email", "locale", "created_at"]
    list_filter = ["locale"]
    search_fields = ["full_name", "phone", "email"]
