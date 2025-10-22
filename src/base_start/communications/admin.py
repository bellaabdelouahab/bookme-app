"""Communications admin."""
from django.contrib import admin

from .models import Notification, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "is_active", "created_at"]
    list_filter = ["channel", "is_active"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient_type", "channel", "status", "sent_at", "created_at"]
    list_filter = ["status", "channel"]
