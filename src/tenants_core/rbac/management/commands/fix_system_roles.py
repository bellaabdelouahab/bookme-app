"""
Management command to update system roles for all existing tenants.

This command updates the permissions for all system roles (Owner, Admin, Manager, Staff, Viewer)
to match the corrected SYSTEM_ROLES_CONFIG in signals.py.

Usage:
    python manage.py fix_system_roles
    python manage.py fix_system_roles --dry-run  # See what would change without making changes
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from tenants_core.tenant.models import Tenant
from tenants_core.rbac.models import TenantRole
from tenants_core.rbac.signals import SYSTEM_ROLES_CONFIG


class Command(BaseCommand):
    help = 'Update system roles for all tenants with corrected permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        self.stdout.write('=' * 80)
        self.stdout.write('Updating System Roles for All Tenants')
        self.stdout.write('=' * 80)

        # Get all tenants
        tenants = Tenant.objects.all().order_by('created_at')
        total_tenants = tenants.count()

        self.stdout.write(f'\nFound {total_tenants} tenant(s) to process\n')

        total_updated = 0
        total_skipped = 0
        total_errors = 0

        for i, tenant in enumerate(tenants, 1):
            self.stdout.write(f'\n[{i}/{total_tenants}] Processing tenant: {tenant.name} ({tenant.schema_name})')
            self.stdout.write('-' * 80)

            updated_count = 0

            for role_name, role_config in SYSTEM_ROLES_CONFIG.items():
                try:
                    # Find the system role for this tenant
                    role = TenantRole.objects.filter(
                        tenant_id=tenant.id,
                        name=role_name,
                        is_system=True
                    ).first()

                    if not role:
                        self.stdout.write(
                            self.style.WARNING(f'  [!] Role "{role_name}" not found - skipping')
                        )
                        total_skipped += 1
                        continue

                    # Check if permissions need updating
                    current_perms = set(role.permissions or [])
                    new_perms = set(role_config['permissions'])

                    if current_perms == new_perms:
                        self.stdout.write(f'  [OK] {role_name}: Already up to date')
                        continue

                    # Calculate changes
                    added = new_perms - current_perms
                    removed = current_perms - new_perms

                    self.stdout.write(f'  [UPDATE] {role_name}:')
                    self.stdout.write(f'    Current: {len(current_perms)} permissions')
                    self.stdout.write(f'    New:     {len(new_perms)} permissions')

                    if added:
                        self.stdout.write(self.style.SUCCESS(f'    Added:   {len(added)} permissions'))
                        for perm in sorted(added):
                            self.stdout.write(f'             + {perm}')

                    if removed:
                        self.stdout.write(self.style.WARNING(f'    Removed: {len(removed)} permissions'))
                        for perm in sorted(removed):
                            self.stdout.write(f'             - {perm}')

                    if not dry_run:
                        with transaction.atomic():
                            role.permissions = role_config['permissions']
                            role.description = role_config['description']
                            role.save()
                        self.stdout.write(self.style.SUCCESS('    [SAVED]'))
                    else:
                        self.stdout.write(self.style.WARNING('    [DRY RUN - NOT SAVED]'))

                    updated_count += 1
                    total_updated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  [ERROR] Failed to update {role_name}: {str(e)}')
                    )
                    total_errors += 1

            if updated_count == 0:
                self.stdout.write(self.style.SUCCESS(f'  All roles up to date for {tenant.name}'))

        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('Summary')
        self.stdout.write('=' * 80)
        self.stdout.write(f'Tenants processed: {total_tenants}')
        self.stdout.write(f'Roles updated:     {total_updated}')
        self.stdout.write(f'Roles skipped:     {total_skipped}')
        self.stdout.write(f'Errors:            {total_errors}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN COMPLETE - No changes were made'))
            self.stdout.write('Run without --dry-run to apply these changes')
        else:
            if total_updated > 0:
                self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {total_updated} system roles!'))
            else:
                self.stdout.write(self.style.SUCCESS('\nAll system roles were already up to date!'))

        self.stdout.write('=' * 80)
