"""
Management command to list all tenants and their domains.
"""
from django.core.management.base import BaseCommand
from django.db import connection

from tenants_core.tenant.models import Domain, Tenant


class Command(BaseCommand):
    help = 'List all tenants and their domains'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['simple', 'detailed', 'urls'],
            default='detailed',
            help='Output format',
        )

    def handle(self, *args, **options):
        format_type = options['format']

        tenants = Tenant.objects.all().order_by('schema_name')
        count = tenants.count()

        if count == 0:
            self.stdout.write(self.style.WARNING('No tenants found'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {count} tenant(s):\n'))

        for tenant in tenants:
            domains = Domain.objects.filter(tenant=tenant)

            if format_type == 'simple':
                self._print_simple(tenant, domains)
            elif format_type == 'urls':
                self._print_urls(tenant, domains)
            else:
                self._print_detailed(tenant, domains)

        self.stdout.write('')

    def _print_simple(self, tenant, domains):
        """Simple format: schema_name -> domain"""
        domain_str = ', '.join([d.domain for d in domains])
        self.stdout.write(f'{tenant.schema_name} -> {domain_str}')

    def _print_urls(self, tenant, domains):
        """URLs format: clickable URLs"""
        for domain in domains:
            url = f'http://{domain.domain}:8000'
            self.stdout.write(f'  {url}')

    def _print_detailed(self, tenant, domains):
        """Detailed format: all info"""
        self.stdout.write(self.style.SUCCESS(f'━━━ {tenant.name} ━━━'))
        self.stdout.write(f'  Schema: {self.style.WARNING(tenant.schema_name)}')
        self.stdout.write(f'  App Type: {tenant.app_type or "N/A"}')
        self.stdout.write(f'  Created: {tenant.created_at}')

        if domains:
            self.stdout.write(f'  Domains:')
            for domain in domains:
                primary = ' (PRIMARY)' if domain.is_primary else ''
                url = f'http://{domain.domain}:8000'
                self.stdout.write(
                    f'    • {self.style.HTTP_INFO(domain.domain)}{primary}'
                )
                self.stdout.write(f'      {url}')
        else:
            self.stdout.write(self.style.ERROR('  ⚠ No domains configured!'))

        self.stdout.write('')
