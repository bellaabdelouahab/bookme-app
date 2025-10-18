"""User admin interface."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import TenantMembership, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_active", "is_staff", "created_at"]
    list_filter = ["is_active", "is_staff", "is_superuser", "created_at"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "tenant_id", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active", "joined_at"]
    search_fields = ["user__email", "tenant_id"]
    readonly_fields = ["joined_at", "updated_at"]
