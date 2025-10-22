"""
Management command to convert tenant domains to .localhost for development.
"""
from django.core.management.base import BaseCommand

from tenants_core.tenant.models import Domain


class Command(BaseCommand):
    help = 'Convert tenant domains from .bookme.ma to .localhost for local development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reverse',
            action='store_true',
            help='Convert .localhost back to .bookme.ma',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reverse = options['reverse']

        if reverse:
            from_suffix = '.localhost'
            to_suffix = '.bookme.ma'
            self.stdout.write(self.style.WARNING(
                'Converting .localhost domains to .bookme.ma...'
            ))
        else:
            from_suffix = '.bookme.ma'
            to_suffix = '.localhost'
            self.stdout.write(self.style.SUCCESS(
                'Converting .bookme.ma domains to .localhost...'
            ))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))

        domains = Domain.objects.filter(domain__contains=from_suffix)
        count = domains.count()

        if count == 0:
            self.stdout.write(self.style.WARNING(
                f'No domains found with {from_suffix}'
            ))
            return

        self.stdout.write(f'Found {count} domain(s) to update:\n')

        for domain in domains:
            old_domain = domain.domain
            new_domain = old_domain.replace(from_suffix, to_suffix)

            self.stdout.write(
                f'  {self.style.WARNING(old_domain)} -> {self.style.SUCCESS(new_domain)}'
            )

            if not dry_run:
                domain.domain = new_domain
                domain.save()

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully updated {count} domain(s)')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN: {count} domain(s) would be updated')
            )
            self.stdout.write('Run without --dry-run to apply changes')
