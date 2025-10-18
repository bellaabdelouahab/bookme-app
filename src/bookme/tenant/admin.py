"""
Tenant admin interface.
"""
from django.contrib import admin

from .models import Domain, Tenant, TenantConfig, TenantLifecycle


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "schema_name",
        "primary_domain",
        "status",
        "subscription_tier",
        "created_at",
    ]
    list_filter = ["status", "subscription_tier", "created_at"]
    search_fields = ["name", "schema_name", "primary_domain", "contact_email"]
    readonly_fields = ["schema_name", "created_at", "updated_at"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "schema_name",
                    "primary_domain",
                    "status",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_email",
                    "contact_phone",
                )
            },
        ),
        (
            "Subscription & Limits",
            {
                "fields": (
                    "subscription_tier",
                    "max_staff",
                    "max_services",
                    "max_bookings_per_month",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": ("metadata",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ["domain", "tenant", "is_primary"]
    list_filter = ["is_primary"]
    search_fields = ["domain", "tenant__name"]


@admin.register(TenantConfig)
class TenantConfigAdmin(admin.ModelAdmin):
    list_display = ["tenant", "category", "key", "is_encrypted", "updated_at"]
    list_filter = ["category", "is_encrypted"]
    search_fields = ["tenant__name", "key"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TenantLifecycle)
class TenantLifecycleAdmin(admin.ModelAdmin):
    list_display = ["tenant", "event", "performed_by", "occurred_at"]
    list_filter = ["event", "occurred_at"]
    search_fields = ["tenant__name", "performed_by"]
    readonly_fields = ["occurred_at"]
    date_hierarchy = "occurred_at"
