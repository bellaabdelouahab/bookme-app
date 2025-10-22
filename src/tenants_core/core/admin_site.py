"""Custom AdminSite for the public (super admin) domain.

This site registers only shared models to avoid querying tenant-only tables
on the public schema.
"""
from django.contrib.admin import AdminSite

# Local imports (admin classes then models)
from tenants_core.tenant.admin import (
    DomainAdmin,
    TenantAdmin,
    TenantConfigAdmin,
    TenantLifecycleAdmin,
)
from tenants_core.users.admin import TenantMembershipAdmin, UserAdmin
from tenants_core.tenant.models import Domain, Tenant, TenantConfig, TenantLifecycle
from tenants_core.users.models import TenantMembership, User

class PublicAdminSite(AdminSite):
    site_header = "BookMe Platform Admin"
    site_title = "BookMe Platform Admin"
    index_title = "Platform Administration"

    def has_permission(self, request):
        """
        Allow access to:
        1. Superusers (full access to everything)
        2. Platform staff (access controlled by Django groups/permissions)
        """
        return bool(
            request.user
            and request.user.is_active
            and (request.user.is_superuser or getattr(request.user, 'is_platform_staff', False))
        )


# Instantiate a separate AdminSite for the public domain
public_admin_site = PublicAdminSite(name="public_admin")


# Register using the same ModelAdmin classes
public_admin_site.register(Tenant, TenantAdmin)
public_admin_site.register(Domain, DomainAdmin)
public_admin_site.register(TenantConfig, TenantConfigAdmin)
public_admin_site.register(TenantLifecycle, TenantLifecycleAdmin)
public_admin_site.register(User, UserAdmin)
public_admin_site.register(TenantMembership, TenantMembershipAdmin)
