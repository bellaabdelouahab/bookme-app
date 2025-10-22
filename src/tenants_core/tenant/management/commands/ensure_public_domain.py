"""Ensure the public domain exists for local development or custom hosts.

Usage:
    python manage.py ensure_public_domain --host localhost --host 127.0.0.1
If no --host is provided, defaults to ['localhost'].
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from tenants_core.tenant.models import Domain, Tenant


class Command(BaseCommand):
    help = "Ensure Domain entries exist for the public tenant for given hostnames."

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            action="append",
            dest="hosts",
            default=None,
            help="Hostname to map to the public schema (can be provided multiple times)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        hosts: list[str] = options.get("hosts") or ["localhost"]

        # Get or create the public tenant row (schema exists by default)
        public_tenant = Tenant.objects.filter(schema_name="public").first()
        if not public_tenant:
            primary = hosts[0] if hosts else "localhost"
            self.stdout.write(
                self.style.WARNING(
                    "Public tenant not found. Creating a Tenant row for schema 'public'."
                )
            )
            # Create a minimal public tenant object and avoid creating schema on save
            public_tenant = Tenant(
                name="Public",
                schema_name="public",
                contact_email="admin@localhost",
                contact_phone="",
                primary_domain=primary,
            )
            # Prevent schema creation for the already-existing 'public' schema
            try:
                public_tenant.auto_create_schema = False  # attribute provided by TenantMixin
            except Exception:
                pass
            public_tenant.save()

        created = 0
        for h in hosts:
            domain, was_created = Domain.objects.get_or_create(
                domain=h,
                defaults={
                    "tenant": public_tenant,
                    "is_primary": False,
                },
            )
            # If it existed but pointed elsewhere, realign it to public tenant
            if not was_created and domain.tenant_id != public_tenant.id:
                domain.tenant = public_tenant
                domain.is_primary = False
                domain.save(update_fields=["tenant", "is_primary"])
                self.stdout.write(self.style.WARNING(f"Repointed existing domain '{h}' to public"))
            elif was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created domain '{h}' for public"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Ensured {len(hosts)} host(s); created {created}. You can now access /admin on those hosts."
            )
        )
