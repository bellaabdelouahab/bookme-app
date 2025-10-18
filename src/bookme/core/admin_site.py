"""Custom AdminSite for the public (super admin) domain.

This site registers only shared models to avoid querying tenant-only tables
on the public schema.
"""
from django.contrib.admin import AdminSite

# Local imports (admin classes then models)
from bookme.tenant.admin import (
    DomainAdmin,
    TenantAdmin,
    TenantConfigAdmin,
    TenantLifecycleAdmin,
)
from bookme.users.admin import TenantMembershipAdmin, UserAdmin
from bookme.tenant.models import Domain, Tenant, TenantConfig, TenantLifecycle
from bookme.users.models import TenantMembership, User

class PublicAdminSite(AdminSite):
    site_header = "BookMe Super Admin"
    site_title = "BookMe Super Admin"
    index_title = "Platform Administration"

    def has_permission(self, request):
        # Limit the public admin to active superusers only
        return bool(request.user and request.user.is_active and request.user.is_superuser)


# Instantiate a separate AdminSite for the public domain
public_admin_site = PublicAdminSite(name="public_admin")


# Register using the same ModelAdmin classes
public_admin_site.register(Tenant, TenantAdmin)
public_admin_site.register(Domain, DomainAdmin)
public_admin_site.register(TenantConfig, TenantConfigAdmin)
public_admin_site.register(TenantLifecycle, TenantLifecycleAdmin)
public_admin_site.register(User, UserAdmin)
public_admin_site.register(TenantMembership, TenantMembershipAdmin)
