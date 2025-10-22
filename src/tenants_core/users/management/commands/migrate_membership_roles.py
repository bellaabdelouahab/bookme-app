"""
Management command to migrate legacy role memberships to use tenant_role FK.

Run with: python manage.py migrate_membership_roles
"""

from django.core.management.base import BaseCommand
from django.db import connection
from tenants_core.users.models import TenantMembership
from tenants_core.rbac.models import TenantRole
from tenants_core.tenant.models import Tenant


class Command(BaseCommand):
    help = 'Migrate TenantMembership records from legacy role CharField to tenant_role FK'

    ROLE_MAPPING = {
        'owner': 'owner',
        'admin': 'admin',
        'manager': 'manager',
        'staff': 'staff',
        'viewer': 'viewer',
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Only process specific tenant by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )

    def handle(self, *args, **options):
        tenant_id_filter = options.get('tenant_id')
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        self.stdout.write(self.style.SUCCESS('MIGRATING TENANT MEMBERSHIPS TO TENANT ROLES'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))

        # Get tenants
        tenants = Tenant.objects.exclude(schema_name='public')

        if tenant_id_filter:
            tenants = tenants.filter(id=tenant_id_filter)
            if not tenants.exists():
                self.stdout.write(self.style.ERROR(f'Tenant with ID {tenant_id_filter} not found'))
                return

        total_migrated = 0
        total_skipped = 0
        total_errors = 0

        for tenant in tenants:
            self.stdout.write(f'\nProcessing: {tenant.name} (ID: {tenant.id})')
            connection.set_tenant(tenant)

            # Get memberships without tenant_role
            memberships = TenantMembership.objects.filter(tenant_role__isnull=True)
            count = memberships.count()

            if count == 0:
                self.stdout.write('  No memberships to migrate')
                continue

            self.stdout.write(f'  Found {count} membership(s) to migrate')

            for membership in memberships:
                # Get legacy role
                legacy_role = membership.role.lower() if membership.role else None

                if not legacy_role:
                    self.stdout.write(
                        self.style.WARNING(f'    SKIP: {membership.user.email} - No legacy role')
                    )
                    total_skipped += 1
                    continue

                # Map to role_type
                role_type = self.ROLE_MAPPING.get(legacy_role, 'staff')

                # Find matching TenantRole
                try:
                    tenant_role = TenantRole.objects.get(
                        tenant_id=tenant.id,
                        role_type=role_type
                    )

                    if not dry_run:
                        membership.tenant_role = tenant_role
                        membership.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    {"WOULD MIGRATE" if dry_run else "MIGRATED"}: '
                            f'{membership.user.email} -> {tenant_role.name}'
                        )
                    )
                    total_migrated += 1

                except TenantRole.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'    ERROR: {membership.user.email} - '
                            f'Role "{role_type}" not found for tenant {tenant.id}'
                        )
                    )
                    self.stdout.write(
                        self.style.ERROR(
                            f'           Run "python manage.py ensure_system_roles" first'
                        )
                    )
                    total_errors += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    ERROR: {membership.user.email} - {str(e)}')
                    )
                    total_errors += 1

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'  Migrated: {total_migrated}')
        self.stdout.write(f'  Skipped: {total_skipped}')
        self.stdout.write(f'  Errors: {total_errors}')
        if dry_run:
            self.stdout.write(self.style.WARNING('\n  DRY RUN - Re-run without --dry-run to apply changes'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))
