"""Custom AdminSite for public schema with shared models only."""

from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from tenants_core.tenant.admin import (
    DomainAdmin,
    TenantAdmin,
    TenantConfigAdmin,
    TenantLifecycleAdmin,
)
from tenants_core.tenant.models import Domain, Tenant, TenantConfig, TenantLifecycle
from tenants_core.users.admin import TenantMembershipAdmin, UserAdmin
from tenants_core.users.models import TenantMembership, User


class PublicAdminSite(AdminSite):
    site_header = "BookMe Platform Admin"
    site_title = "BookMe Platform Admin"
    index_title = "Platform Administration"

    def has_permission(self, request):
        return bool(
            request.user
            and request.user.is_active
            and (request.user.is_superuser or getattr(request.user, 'is_platform_staff', False))
        )


public_admin_site = PublicAdminSite(name="public_admin")

public_admin_site.register(Tenant, TenantAdmin)
public_admin_site.register(Domain, DomainAdmin)
public_admin_site.register(TenantConfig, TenantConfigAdmin)
public_admin_site.register(TenantLifecycle, TenantLifecycleAdmin)
public_admin_site.register(User, UserAdmin)
public_admin_site.register(TenantMembership, TenantMembershipAdmin)
public_admin_site.register(Group, GroupAdmin)
