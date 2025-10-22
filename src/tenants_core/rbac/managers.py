"""
Tenant-scoped managers and querysets for RBAC models.

These ensure that TenantRole and related models are automatically
filtered by tenant_id to prevent cross-tenant data access.
"""
from django.db import models
from django_tenants.utils import get_tenant_model, schema_context


class TenantScopedQuerySet(models.QuerySet):
    """
    QuerySet that automatically filters by current tenant_id.

    Used for models in the SHARED schema that need tenant scoping
    (like TenantRole).
    """

    def for_tenant(self, tenant_id):
        """Explicitly filter by a specific tenant ID."""
        return self.filter(tenant_id=tenant_id)

    def current_tenant(self):
        """
        Filter by the current tenant from the connection.

        Note: This works when accessed from a tenant schema context.
        For SHARED schema models accessed from tenant requests, you should
        pass tenant_id explicitly via for_tenant().
        """
        try:
            from django.db import connection
            tenant = connection.tenant
            if tenant and hasattr(tenant, 'id'):
                return self.filter(tenant_id=tenant.id)
        except (AttributeError, RuntimeError):
            pass
        return self


class TenantScopedManager(models.Manager):
    """
    Manager that uses TenantScopedQuerySet.

    Usage in models:
        objects = TenantScopedManager()
    """

    def get_queryset(self):
        return TenantScopedQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant_id):
        """Get objects for a specific tenant."""
        return self.get_queryset().for_tenant(tenant_id)

    def current_tenant(self):
        """Get objects for the current tenant from connection."""
        return self.get_queryset().current_tenant()


class TenantRoleManager(TenantScopedManager):
    """
    Specialized manager for TenantRole with additional helper methods.
    """

    def get_system_roles(self, tenant_id):
        """Get all system roles for a tenant."""
        return self.for_tenant(tenant_id).filter(is_system=True)

    def get_custom_roles(self, tenant_id):
        """Get all custom (non-system) roles for a tenant."""
        return self.for_tenant(tenant_id).filter(is_system=False)

    def get_active_roles(self, tenant_id):
        """Get all active roles for a tenant."""
        return self.for_tenant(tenant_id).filter(is_active=True)

    def get_role_by_type(self, tenant_id, role_type):
        """
        Get a role by its type for a tenant.

        Args:
            tenant_id: UUID of the tenant
            role_type: One of TenantRole.RoleType choices (owner, admin, etc.)
        """
        return self.for_tenant(tenant_id).filter(role_type=role_type).first()

    def create_role(self, tenant_id, name, permissions=None, **kwargs):
        """
        Create a new role for a tenant.

        Args:
            tenant_id: UUID of the tenant
            name: Name of the role
            permissions: List of permission codenames
            **kwargs: Additional fields (description, role_type, etc.)
        """
        if permissions is None:
            permissions = []

        return self.create(
            tenant_id=tenant_id,
            name=name,
            permissions=permissions,
            **kwargs
        )
