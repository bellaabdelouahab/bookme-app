"""
RBAC models for tenant-scoped role and permission management.
"""
import uuid

from django.contrib.auth.models import Permission
from django.db import models

from .managers import TenantRoleManager


class TenantRole(models.Model):
    """
    Role model for tenant-specific permissions.

    Stored in the SHARED schema but scoped by tenant_id.
    Each tenant can create custom roles in addition to system roles.
    System roles (Owner, Admin, Manager, Staff, Viewer) are protected.
    """

    class RoleType(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Administrator"
        MANAGER = "manager", "Manager"
        STAFF = "staff", "Staff"
        VIEWER = "viewer", "Viewer"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Foreign key to Tenant (stored as UUID to avoid circular imports)
    tenant_id = models.UUIDField(db_index=True, help_text="ID of the tenant this role belongs to")

    name = models.CharField(
        max_length=100,
        help_text="Role name (e.g., 'Manager', 'Receptionist', 'Therapist')"
    )

    role_type = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.CUSTOM,
        help_text="Type of role - system roles are protected from modification"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of what this role can do"
    )

    # Store Django permission codenames as JSON array
    # e.g., ["add_service", "change_service", "view_booking"]
    permissions = models.JSONField(
        default=list,
        help_text="Array of Django permission codenames this role grants"
    )

    is_system = models.BooleanField(
        default=False,
        db_index=True,
        help_text="System roles cannot be deleted or have their type changed"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Inactive roles cannot be assigned to users"
    )

    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional role configuration (e.g., UI permissions, feature flags)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use tenant-scoped manager
    objects = TenantRoleManager()

    class Meta:
        db_table = "rbac_tenant_role"
        unique_together = [["tenant_id", "name"]]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "role_type"]),
            models.Index(fields=["is_system"]),
        ]
        verbose_name = "Tenant Role"
        verbose_name_plural = "Tenant Roles"

    def __str__(self):
        return self.name

    def get_permission_objects(self):
        """
        Get Django Permission objects for this role's permission codenames.
        """
        if not self.permissions:
            return Permission.objects.none()
        return Permission.objects.filter(codename__in=self.permissions)

    def has_permission(self, permission_codename):
        """
        Check if this role has a specific permission.

        Args:
            permission_codename: String like 'add_service' or 'change_booking'
        """
        return permission_codename in self.permissions

    def add_permission(self, permission_codename):
        """Add a permission to this role."""
        if permission_codename not in self.permissions:
            self.permissions.append(permission_codename)
            self.save(update_fields=["permissions", "updated_at"])

    def remove_permission(self, permission_codename):
        """Remove a permission from this role."""
        if permission_codename in self.permissions:
            self.permissions.remove(permission_codename)
            self.save(update_fields=["permissions", "updated_at"])

    def save(self, *args, **kwargs):
        """
        Validate that system roles maintain their integrity.
        """
        if self.pk:  # Updating existing role
            try:
                old_role = TenantRole.objects.get(pk=self.pk)
                if old_role.is_system:
                    # Prevent changing role_type of system roles
                    if old_role.role_type != self.role_type:
                        raise ValueError(
                            f"Cannot change role_type of system role '{old_role.name}'"
                        )
                    # System roles cannot be deactivated
                    if not self.is_active and old_role.is_active:
                        raise ValueError(
                            f"Cannot deactivate system role '{old_role.name}'"
                        )
            except TenantRole.DoesNotExist:
                pass

        super().save(*args, **kwargs)
