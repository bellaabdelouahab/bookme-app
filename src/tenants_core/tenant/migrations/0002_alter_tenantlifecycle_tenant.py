from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tenantlifecycle",
            name="tenant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                to="tenant.tenant",
                related_name="lifecycle_events",
                null=True,
                blank=True,
            ),
        ),
    ]
