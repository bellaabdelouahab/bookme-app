"""
Management command to ensure all tenants have system roles.

Run with: python manage.py ensure_system_roles
"""

import uuid
from django.core.management.base import BaseCommand
from tenants_core.rbac.models import TenantRole
from tenants_core.tenant.models import Tenant


class Command(BaseCommand):
    help = 'Ensure all tenants have system roles (Owner, Admin, Manager, Staff, Viewer)'

    SYSTEM_ROLES = {
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
            'description': 'Administrative access to manage users, staff, services, and bookings. Cannot modify billing or critical settings.',
            'permissions': [
                # User management (limited)
                'add_user', 'change_user', 'view_user',
                'add_tenantmembership', 'change_tenantmembership', 'view_tenantmembership',
                # View roles (cannot edit)
                'view_tenantrole',
                # Tenant settings (view only)
                'view_tenant',
                # Services
                'add_service', 'change_service', 'delete_service', 'view_service',
                # Staff
                'add_staffmember', 'change_staffmember', 'delete_staffmember', 'view_staffmember',
                # Customers
                'add_customer', 'change_customer', 'delete_customer', 'view_customer',
                # Bookings
                'add_booking', 'change_booking', 'delete_booking', 'view_booking',
                # Communications
                'add_notification', 'change_notification', 'view_notification',
                # Payments (view only)
                'view_payment',
                # Resources
                'add_resource', 'change_resource', 'delete_resource', 'view_resource',
            ]
        },
        'Manager': {
            'role_type': 'manager',
            'description': 'Manage daily operations including bookings, customers, and staff schedules. Cannot modify settings or users.',
            'permissions': [
                # View users
                'view_user', 'view_tenantmembership',
                # Services (view and edit)
                'change_service', 'view_service',
                # Staff (view and schedule)
                'change_staffmember', 'view_staffmember',
                # Customers
                'add_customer', 'change_customer', 'view_customer',
                # Bookings
                'add_booking', 'change_booking', 'delete_booking', 'view_booking',
                # Communications
                'add_notification', 'view_notification',
                # Payments (view only)
                'view_payment',
                # Resources
                'change_resource', 'view_resource',
            ]
        },
        'Staff': {
            'role_type': 'staff',
            'description': 'Staff member access to view schedule, manage assigned bookings, and view customer information.',
            'permissions': [
                # View users
                'view_user',
                # Services (view only)
                'view_service',
                # Staff (view own profile)
                'view_staffmember',
                # Customers (view only)
                'view_customer',
                # Bookings (limited)
                'change_booking', 'view_booking',
                # Communications (view only)
                'view_notification',
                # Resources (view only)
                'view_resource',
            ]
        },
        'Viewer': {
            'role_type': 'viewer',
            'description': 'Read-only access to view bookings, customers, and reports. Cannot make any changes.',
            'permissions': [
                # View only
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

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing system role permissions to latest definition',
        )
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Only process specific tenant by ID',
        )

    def handle(self, *args, **options):
        update_existing = options['update']
        tenant_id_filter = options.get('tenant_id')

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('ENSURING SYSTEM ROLES FOR ALL TENANTS'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))

        # Get tenants
        tenants = Tenant.objects.exclude(schema_name='public')

        if tenant_id_filter:
            tenants = tenants.filter(id=tenant_id_filter)
            if not tenants.exists():
                self.stdout.write(self.style.ERROR(f'Tenant with ID {tenant_id_filter} not found'))
                return

        self.stdout.write(f'Processing {tenants.count()} tenant(s)...\n')

        total_created = 0
        total_updated = 0
        total_skipped = 0

        for tenant in tenants:
            self.stdout.write(f'\nTenant: {tenant.name} (ID: {tenant.id})')

            for role_name, role_config in self.SYSTEM_ROLES.items():
                # Check if exists
                existing_role = TenantRole.objects.filter(
                    tenant_id=tenant.id,
                    name=role_name
                ).first()

                if existing_role:
                    if update_existing:
                        existing_role.permissions = role_config['permissions']
                        existing_role.description = role_config['description']
                        existing_role.role_type = role_config['role_type']
                        existing_role.is_system = True
                        existing_role.is_active = True
                        existing_role.save()
                        self.stdout.write(
                            self.style.WARNING(f'  - {role_name}: UPDATED ({len(role_config["permissions"])} permissions)')
                        )
                        total_updated += 1
                    else:
                        self.stdout.write(f'  - {role_name}: EXISTS (use --update to refresh)')
                        total_skipped += 1
                else:
                    # Create new role
                    TenantRole.objects.create(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        name=role_name,
                        role_type=role_config['role_type'],
                        description=role_config['description'],
                        permissions=role_config['permissions'],
                        is_system=True,
                        is_active=True,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'  - {role_name}: CREATED ({len(role_config["permissions"])} permissions)')
                    )
                    total_created += 1

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'  Created: {total_created}')
        self.stdout.write(f'  Updated: {total_updated}')
        self.stdout.write(f'  Skipped: {total_skipped}')
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))
