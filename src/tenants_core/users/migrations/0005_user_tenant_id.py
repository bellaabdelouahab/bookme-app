# Generated migration for adding tenant_id to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_clean_rbac_only_approach'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tenant_id',
            field=models.UUIDField(
                blank=True,
                db_index=True,
                help_text="Tenant this user belongs to. NULL for public users or users managed via TenantMembership.",
                null=True,
                verbose_name='Tenant'
            ),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['tenant_id'], name='users_user_tenant__idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['tenant_id', 'is_active'], name='users_user_tenant__active_idx'),
        ),
    ]
