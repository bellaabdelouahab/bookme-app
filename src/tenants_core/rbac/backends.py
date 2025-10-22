"""Tenant-scoped RBAC permission backend."""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission
from django.db import connection

from tenants_core.rbac.models import TenantRole
from tenants_core.users.models import User


class TenantRolePermissionBackend(BaseBackend):
    """Check permissions from TenantRole via TenantMembership."""

    def authenticate(self, request, **kwargs):
        return None

    def get_user_permissions(self, user_obj: User, obj=None) -> set[str]:
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        if user_obj.is_superuser:
            return self._get_all_permissions()

        tenant = getattr(connection, 'tenant', None)
        if not tenant or not hasattr(tenant, 'id') or tenant.schema_name == 'public':
            return set()

        try:
            from tenants_core.users.models import TenantMembership
            membership = TenantMembership.objects.get(
                user=user_obj,
                tenant_id=tenant.id,
                is_active=True
            )

            if membership.tenant_role and membership.tenant_role.is_active:
                return self._format_permissions(membership.tenant_role.permissions or [])

            return self._format_permissions(membership.permissions or [])

        except TenantMembership.DoesNotExist:
            return set()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Error getting permissions for user {user_obj.id}: {e}"
            )
            return set()

    def _format_permissions(self, permission_codenames: list) -> set[str]:
        if not permission_codenames:
            return set()

        from django_tenants.utils import schema_context

        with schema_context('public'):
            permissions = Permission.objects.filter(
                codename__in=permission_codenames
            ).select_related('content_type').values_list(
                'content_type__app_label', 'codename'
            )
            return {f"{app_label}.{codename}" for app_label, codename in permissions}

    def get_all_permissions(self, user_obj: User, obj=None) -> set[str]:
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        if not hasattr(user_obj, '_tenant_perm_cache'):
            user_obj._tenant_perm_cache = self.get_user_permissions(user_obj)

        return user_obj._tenant_perm_cache

    def has_perm(self, user_obj: User, perm: str, obj=None) -> bool:
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        if user_obj.is_superuser:
            return True

        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj: User, app_label: str) -> bool:
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        if user_obj.is_superuser:
            return True

        perms = self.get_all_permissions(user_obj)
        return any(perm.startswith(f"{app_label}.") for perm in perms)

    def _get_all_permissions(self) -> set[str]:
        return {
            f"{p.content_type.app_label}.{p.codename}"
            for p in Permission.objects.select_related('content_type').all()
        }

    def get_user_role(self, user_obj: User) -> TenantRole | None:
        if not user_obj.is_active or user_obj.is_anonymous:
            return None

        tenant = getattr(connection, 'tenant', None)
        if not tenant:
            return None

        try:
            from tenants_core.users.models import TenantMembership
            membership = TenantMembership.objects.get(
                user=user_obj,
                tenant_id=tenant.id,
                is_active=True
            )
            return membership.tenant_role
        except TenantMembership.DoesNotExist:
            return None
