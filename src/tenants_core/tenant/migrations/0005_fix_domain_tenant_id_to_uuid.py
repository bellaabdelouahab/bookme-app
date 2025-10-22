# Generated manually on 2025-10-21
# Fix tenant_domain.tenant_id to match tenant_tenant.id (UUID)

from django.db import migrations


def convert_domain_tenant_ids(apps, schema_editor):
    """
    Convert tenant_domain.tenant_id from bigint to UUID to match tenant_tenant.id
    """
    with schema_editor.connection.cursor() as cursor:
        # Step 1: Add a new UUID column
        cursor.execute("""
            ALTER TABLE public.tenant_domain
            ADD COLUMN new_tenant_id UUID;
        """)

        # Step 2: Copy data with conversion (bigint -> UUID format)
        # Convert integer ID to UUID format: 00000000-0000-0000-0000-{hex:012x}
        cursor.execute("""
            UPDATE public.tenant_domain
            SET new_tenant_id = CAST(
                '00000000-0000-0000-0000-' || LPAD(TO_HEX(tenant_id), 12, '0')
                AS UUID
            );
        """)

        # Step 3: Drop the old column and foreign key
        cursor.execute("""
            ALTER TABLE public.tenant_domain
            DROP COLUMN tenant_id CASCADE;
        """)

        # Step 4: Rename new column to tenant_id
        cursor.execute("""
            ALTER TABLE public.tenant_domain
            RENAME COLUMN new_tenant_id TO tenant_id;
        """)

        # Step 5: Make it NOT NULL
        cursor.execute("""
            ALTER TABLE public.tenant_domain
            ALTER COLUMN tenant_id SET NOT NULL;
        """)

        # Step 6: Recreate the foreign key
        cursor.execute("""
            ALTER TABLE public.tenant_domain
            ADD CONSTRAINT tenant_domain_tenant_id_fkey
            FOREIGN KEY (tenant_id) REFERENCES public.tenant_tenant(id)
            ON DELETE CASCADE;
        """)

        # Step 7: Recreate the index
        cursor.execute("""
            CREATE INDEX tenant_domain_tenant_id_idx
            ON public.tenant_domain(tenant_id);
        """)

        print("Successfully converted tenant_domain.tenant_id to UUID")


class Migration(migrations.Migration):

    dependencies = [
        ("tenant", "0004_change_tenant_id_to_uuid"),
    ]

    operations = [
        migrations.RunPython(convert_domain_tenant_ids, migrations.RunPython.noop),
    ]
