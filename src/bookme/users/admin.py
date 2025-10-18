"""User admin interface."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from bookme.tenant.models import Tenant

from .forms import TenantMembershipAdminForm
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
    form = TenantMembershipAdminForm
    list_display = ["user", "tenant_display", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active", "joined_at"]
    search_fields = ["user__email", "tenant_id"]
    readonly_fields = ["joined_at", "updated_at"]

    def tenant_display(self, obj):
        try:
            tenant = Tenant.objects.get(id=obj.tenant_id)
            return f"{tenant.name} ({tenant.primary_domain})"
        except Tenant.DoesNotExist:
            return str(obj.tenant_id)
    tenant_display.short_description = "Tenant"
