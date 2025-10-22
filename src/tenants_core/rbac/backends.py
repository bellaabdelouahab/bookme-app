"""
Custom authentication backend for tenant-scoped role-based permissions.

This backend integrates with Django's permission system to check permissions
based on TenantRole assignments via TenantMembership.
"""
from typing import Set, Optional
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission
from django.db import connection
from tenants_core.rbac.models import TenantRole
from tenants_core.users.models import User


class TenantRolePermissionBackend(BaseBackend):
    """
    Permission backend that checks permissions from TenantRole via TenantMembership.

    This backend:
    1. Gets the user's TenantMembership for the current tenant (from connection.tenant)
    2. Retrieves the assigned TenantRole
    3. Returns permissions from the role's permissions JSONField
    4. Ensures tenant isolation - only checks permissions for current tenant

    Usage:
        Add to settings.py:
        AUTHENTICATION_BACKENDS = [
            'django.contrib.auth.backends.ModelBackend',  # Keep for superuser
            'tenants_core.rbac.backends.TenantRolePermissionBackend',
        ]
    """

    def authenticate(self, request, **kwargs):
        """
        This backend doesn't handle authentication, only permissions.
        Return None to let other backends handle auth.
        """
        return None

    def get_user_permissions(self, user_obj: User, obj=None) -> Set[str]:
        """
        Get permissions for a user in the current tenant context.

        Args:
            user_obj: The User instance
            obj: Optional object for object-level permissions (not used)

        Returns:
            Set of permission strings in format 'app_label.codename'
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        # Superusers bypass RBAC
        if user_obj.is_superuser:
            return self._get_all_permissions()

        # Get current tenant from connection
        tenant = getattr(connection, 'tenant', None)
        if not tenant:
            return set()

        # Skip if in public schema (FakeTenant doesn't have real id)
        if not hasattr(tenant, 'id') or tenant.schema_name == 'public':
            return set()

        try:
            # Get user's membership for current tenant
            from tenants_core.users.models import TenantMembership
            membership = TenantMembership.objects.get(
                user=user_obj,
                tenant_id=tenant.id,
                is_active=True
            )

            # Return permissions from the assigned role
            if membership.tenant_role and membership.tenant_role.is_active:
                # Convert codenames to app_label.codename format
                return self._format_permissions(membership.tenant_role.permissions or [])

            # Fallback to legacy permissions if no role assigned yet
            # (will be removed after data migration)
            return self._format_permissions(membership.permissions or [])

        except TenantMembership.DoesNotExist:
            return set()
        except Exception as e:
            # Log the error but don't crash
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Error getting permissions for user {user_obj.id} in tenant {tenant.id}: {e}"
            )
            return set()

    def _format_permissions(self, permission_codenames: list) -> Set[str]:
        """
        Convert permission codenames to full 'app_label.codename' format.

        Args:
            permission_codenames: List of codenames like ['add_user', 'view_service']

        Returns:
            Set of formatted permissions like {'users.add_user', 'services.view_service'}
        """
        from django.contrib.auth.models import Permission
        from django.db import connection as db_connection
        import logging
        logger = logging.getLogger(__name__)

        if not permission_codenames:
            return set()

        logger.debug(f"[RBAC Backend] Formatting permissions for codenames: {permission_codenames}")
        logger.debug(f"[RBAC Backend] Current schema: {db_connection.schema_name}")

        # Query Permission model to get app_label for each codename
        # Use unfiltered query to get permissions from public schema (SHARED_APPS)
        # The Permission table is in public schema for django-tenants
        from django_tenants.utils import schema_context

        with schema_context('public'):
            permissions = Permission.objects.filter(
                codename__in=permission_codenames
            ).select_related('content_type').values_list(
                'content_type__app_label', 'codename'
            )
            result = {f"{app_label}.{codename}" for app_label, codename in permissions}

        logger.debug(f"[RBAC Backend] Formatted permissions: {result}")

        # Format as app_label.codename
        return result

    def get_all_permissions(self, user_obj: User, obj=None) -> Set[str]:
        """
        Get all permissions for a user (user + group permissions).

        For RBAC, we only check TenantRole permissions (no Django groups in tenant context).
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        # Cache permissions on the user object to avoid repeated queries
        if not hasattr(user_obj, '_tenant_perm_cache'):
            user_obj._tenant_perm_cache = self.get_user_permissions(user_obj)

        return user_obj._tenant_perm_cache

    def has_perm(self, user_obj: User, perm: str, obj=None) -> bool:
        """
        Check if user has a specific permission in the current tenant.

        Args:
            user_obj: The User instance
            perm: Permission string in format 'app_label.codename'
            obj: Optional object for object-level permissions (not used)

        Returns:
            True if user has the permission, False otherwise
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        # Superusers have all permissions
        if user_obj.is_superuser:
            return True

        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj: User, app_label: str) -> bool:
        """
        Check if user has any permissions in the given app.

        Args:
            user_obj: The User instance
            app_label: The app label (e.g., 'bookings', 'customers')

        Returns:
            True if user has any permission for the app
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return False

        if user_obj.is_superuser:
            return True

        perms = self.get_all_permissions(user_obj)
        return any(perm.startswith(f"{app_label}.") for perm in perms)

    def _get_all_permissions(self) -> Set[str]:
        """
        Get all available permissions in the system (for superusers).

        Returns:
            Set of all permission strings
        """
        return {
            f"{p.content_type.app_label}.{p.codename}"
            for p in Permission.objects.select_related('content_type').all()
        }

    def get_user_role(self, user_obj: User) -> Optional['TenantRole']:
        """
        Get the user's TenantRole for the current tenant.

        This is a helper method for views/middleware that need role info.

        Args:
            user_obj: The User instance

        Returns:
            TenantRole instance or None
        """
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
