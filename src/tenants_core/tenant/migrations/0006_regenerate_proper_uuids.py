# Generated manually on 2025-10-21
# Regenerate tenant UUIDs from padded format to proper random UUIDs

import uuid
from django.db import migrations


def regenerate_tenant_uuids(apps, schema_editor):
    """
    Replace padded UUID format (00000000-0000-0000-0000-00000000000e)
    with proper random UUIDs (5d61d7ed-9dd9-4c3d-bb96-20e22ab31f75)

    Strategy: Update one tenant at a time with all its references in a transaction
    """
    with schema_editor.connection.cursor() as cursor:
        print("\n=== Regenerating Tenant UUIDs ===\n")

        # Get all tenants
        cursor.execute("SELECT id, name FROM public.tenant_tenant ORDER BY name")
        tenants = cursor.fetchall()

        for old_uuid, tenant_name in tenants:
            new_uuid = uuid.uuid4()

            print(f"Processing tenant '{tenant_name}':")
            print(f"  Old UUID: {old_uuid}")
            print(f"  New UUID: {new_uuid}")

            # Step 1: Drop FK constraint temporarily to allow updates
            cursor.execute("""
                ALTER TABLE public.tenant_domain
                DROP CONSTRAINT IF EXISTS tenant_domain_tenant_id_fkey;
            """)

            # Step 2: Update the Tenant ID first
            cursor.execute(
                "UPDATE public.tenant_tenant SET id = %s WHERE id = %s",
                [str(new_uuid), str(old_uuid)]
            )

            # Step 3: Update Domain references
            cursor.execute(
                "UPDATE public.tenant_domain SET tenant_id = %s WHERE tenant_id = %s",
                [str(new_uuid), str(old_uuid)]
            )

            # Step 4: Update TenantRole references
            cursor.execute(
                "UPDATE public.rbac_tenant_role SET tenant_id = %s WHERE tenant_id = %s",
                [str(new_uuid), str(old_uuid)]
            )

            # Step 5: Update TenantMembership references
            cursor.execute(
                "UPDATE public.users_tenant_membership SET tenant_id = %s WHERE tenant_id = %s",
                [str(new_uuid), str(old_uuid)]
            )

            # Step 6: Recreate FK constraint
            cursor.execute("""
                ALTER TABLE public.tenant_domain
                ADD CONSTRAINT tenant_domain_tenant_id_fkey
                FOREIGN KEY (tenant_id) REFERENCES public.tenant_tenant(id)
                ON DELETE CASCADE;
            """)

            print(f"  ✓ Successfully migrated!\n")

        print("=== UUID Regeneration Complete! ===\n")


def reverse_migration(apps, schema_editor):
    """
    This is a one-way migration - cannot reverse to padded UUIDs
    """
    print("WARNING: Cannot reverse UUID regeneration!")
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("tenant", "0005_fix_domain_tenant_id_to_uuid"),
    ]

    operations = [
        migrations.RunPython(regenerate_tenant_uuids, reverse_migration),
    ]
