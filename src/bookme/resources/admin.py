"""Resources admin."""
from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["resource_type", "key", "locale", "created_at"]
    list_filter = ["resource_type", "locale"]
    search_fields = ["key"]
