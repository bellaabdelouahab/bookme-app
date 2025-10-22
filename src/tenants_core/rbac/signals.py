"""
Signals for RBAC app.

Automatically creates system roles when new tenants are created.
"""
import logging
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# Define system roles configuration
SYSTEM_ROLES_CONFIG = {
    'Owner': {
        'role_type': 'owner',
        'description': 'Full access to all features and settings. Can manage billing, users, and all business operations.',
        'permissions': [
            # User management
            'add_user', 'change_user', 'view_user',
            'add_tenantmembership', 'change_tenantmembership', 'delete_tenantmembership', 'view_tenantmembership',
            # Role management
            'add_tenantrole', 'change_tenantrole', 'delete_tenantrole', 'view_tenantrole',
            # Tenant settings
            'change_tenant', 'view_tenant',
            # Services
            'add_service', 'change_service', 'delete_service', 'view_service',
            # Staff
            'add_staffmember', 'change_staffmember', 'delete_staffmember', 'view_staffmember',
            # Customers
            'add_customer', 'change_customer', 'delete_customer', 'view_customer',
            # Bookings
            'add_booking', 'change_booking', 'delete_booking', 'view_booking',
            # Communications
            'add_notification', 'change_notification', 'delete_notification', 'view_notification',
            # Payments
            'add_payment', 'change_payment', 'delete_payment', 'view_payment',
            # Resources
            'add_resource', 'change_resource', 'delete_resource', 'view_resource',
        ]
    },
    'Admin': {
        'role_type': 'admin',
        'description': 'Administrative access to manage business operations including services, staff, bookings, and customers.',
        'permissions': [
            'view_user',
            'view_tenantmembership',
            'view_tenantrole',
            'view_tenant',
            'add_service', 'change_service', 'delete_service', 'view_service',
            'add_staffmember', 'change_staffmember', 'delete_staffmember', 'view_staffmember',
            'add_customer', 'change_customer', 'delete_customer', 'view_customer',
            'add_booking', 'change_booking', 'delete_booking', 'view_booking',
            'add_notification', 'change_notification', 'view_notification',
            'view_payment',
            'add_resource', 'change_resource', 'delete_resource', 'view_resource',
        ]
    },
    'Manager': {
        'role_type': 'manager',
        'description': 'Manage daily operations including bookings, customers, and staff schedules.',
        'permissions': [
            'view_user', 'view_tenantmembership',
            'change_service', 'view_service',
            'change_staffmember', 'view_staffmember',
            'add_customer', 'change_customer', 'view_customer',
            'add_booking', 'change_booking', 'delete_booking', 'view_booking',
            'add_notification', 'view_notification',
            'view_payment',
            'change_resource', 'view_resource',
        ]
    },
    'Staff': {
        'role_type': 'staff',
        'description': 'Staff member access to view schedule and manage assigned bookings.',
        'permissions': [
            'view_user',
            'view_service',
            'view_staffmember',
            'view_customer',
            'change_booking', 'view_booking',
            'view_notification',
            'view_payment',
            'view_resource',
        ]
    },
    'Viewer': {
        'role_type': 'viewer',
        'description': 'Read-only access to view bookings, customers, and reports.',
        'permissions': [
            'view_service',
            'view_staffmember',
            'view_customer',
            'view_booking',
            'view_notification',
            'view_payment',
            'view_resource',
        ]
    },
}


@receiver(post_save, sender='tenant.Tenant')
def create_system_roles_for_new_tenant(sender, instance, created, **kwargs):
    """
    Automatically create system roles when a new tenant is created.

    This ensures every tenant has the 5 standard roles:
    - Owner
    - Admin
    - Manager
    - Staff
    - Viewer
    """
    if not created:
        # Only run for new tenants
        return

    # Avoid circular import
    from .models import TenantRole

    tenant = instance
    logger.info(f"Creating system roles for new tenant: {tenant.name} (ID: {tenant.id})")

    roles_created = []

    for role_name, role_config in SYSTEM_ROLES_CONFIG.items():
        try:
            # Check if role already exists (shouldn't happen, but be safe)
            existing = TenantRole.objects.filter(
                tenant_id=tenant.id,
                name=role_name
            ).exists()

            if existing:
                logger.warning(f"  Role '{role_name}' already exists for tenant {tenant.id}, skipping")
                continue

            # Create the role
            role = TenantRole.objects.create(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name=role_name,
                role_type=role_config['role_type'],
                description=role_config['description'],
                permissions=role_config['permissions'],
                is_system=True,
                is_active=True,
            )

            roles_created.append(role_name)
            logger.info(f"  ✓ Created system role: {role_name} ({len(role_config['permissions'])} permissions)")

        except Exception as e:
            logger.error(f"  ✗ Failed to create role '{role_name}' for tenant {tenant.id}: {e}")

    if roles_created:
        logger.info(
            f"Successfully created {len(roles_created)} system roles for tenant '{tenant.name}': "
            f"{', '.join(roles_created)}"
        )
    else:
        logger.warning(f"No system roles were created for tenant '{tenant.name}'")
