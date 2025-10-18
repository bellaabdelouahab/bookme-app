# Database Migration Guide

This guide explains how to safely update the database schema in our multi-tenant application.

## 🎯 Understanding Migration Types

### Shared Migrations
Apply to the **public schema** (shared data):
- `users` - User accounts
- `tenant` - Tenant definitions
- `core` - Core utilities

**Affects**: All tenants (shared tables)

### Tenant Migrations
Apply to **each tenant schema** (isolated data):
- `services` - Service catalog
- `bookings` - Booking records
- `customers` - Customer data
- `staff` - Staff management
- `communications` - Notifications
- `payments` - Payment records
- `resources` - Resource management

**Affects**: Each tenant separately

---

## 📋 Step-by-Step: Adding a New Field

### Example: Add `capacity` field to Service model

#### Step 1: Edit the Model

```python
# src/bookme/services/models.py

from bookme.core.models import TenantAwareModel
from django.db import models

class Service(TenantAwareModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)

    # NEW FIELD
    capacity = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of customers per booking"
    )

    class Meta:
        db_table = "services_service"
        ordering = ["-created_at"]
```

#### Step 2: Create Migration

```powershell
cd src
python manage.py makemigrations services
```

**Output**:
```
Migrations for 'services':
  bookme\services\migrations\0002_service_capacity.py
    - Add field capacity to service
```

#### Step 3: Review Migration File

Django automatically creates a migration file. Review it:

```python
# src/bookme/services/migrations/0002_service_capacity.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='capacity',
            field=models.PositiveIntegerField(default=1, help_text='Maximum number of customers per booking'),
        ),
    ]
```

✅ **Looks good!** The migration will add the field with a default value.

#### Step 4: Apply Migration to All Tenants

```powershell
python manage.py migrate_schemas
```

**Output**:
```
[standard:tenant_demo] === Running migrations
[standard:tenant_demo]   Applying services.0002_service_capacity... OK

[standard:tenant_acme] === Running migrations
[standard:tenant_acme]   Applying services.0002_service_capacity... OK

[standard:tenant_xyz] === Running migrations
[standard:tenant_xyz]   Applying services.0002_service_capacity... OK
```

✅ **Done!** All tenants now have the `capacity` field.

---

## 📋 Step-by-Step: Adding a New Model

### Example: Add ServiceCategory model

#### Step 1: Create the Model

```python
# src/bookme/services/models.py

class ServiceCategory(TenantAwareModel):
    """Categories for organizing services."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "services_category"
        ordering = ["order", "name"]
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name


# Update Service model to reference category
class Service(TenantAwareModel):
    name = models.CharField(max_length=200)
    # ... other fields ...

    # NEW FIELD
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
```

#### Step 2: Register in Admin

```python
# src/bookme/services/admin.py

from django.contrib import admin
from .models import Service, ServiceCategory

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["order", "name"]
```

#### Step 3: Create Migration

```powershell
python manage.py makemigrations services
```

**Output**:
```
Migrations for 'services':
  bookme\services\migrations\0003_servicecategory_service_category.py
    - Create model ServiceCategory
    - Add field category to service
```

#### Step 4: Apply Migration

```powershell
python manage.py migrate_schemas
```

✅ **Done!** New model created in all tenant schemas.

---

## 📋 Step-by-Step: Modifying Existing Data

### Example: Make email field required (was optional)

This is trickier because we need to handle existing null values.

#### Step 1: Create Migration with Default Value

```python
# src/bookme/customers/models.py

class Customer(TenantAwareModel):
    name = models.CharField(max_length=200)
    # Change: remove blank=True, add default temporarily
    email = models.EmailField(default='noemail@example.com')  # Will remove default after migration
    phone = models.CharField(max_length=20, blank=True)
```

#### Step 2: Create Migration

```powershell
python manage.py makemigrations customers
```

Django will ask:
```
You are trying to change the nullable field 'email' on customer to non-nullable
without a default; we can't do that (the database needs something to populate
existing rows).

Please select a fix:
 1) Provide a one-off default now (will be set on all existing rows)
 2) Ignore for now, and let me handle existing rows manually
 3) Quit, and let me add a default in models.py

Select an option: 1
Please enter the default value now, as valid Python
>>> 'unknown@example.com'
```

#### Step 3: Create Data Migration to Clean Up

```powershell
python manage.py makemigrations customers --empty --name cleanup_email_defaults
```

Edit the created migration:

```python
# src/bookme/customers/migrations/0003_cleanup_email_defaults.py

from django.db import migrations

def cleanup_default_emails(apps, schema_editor):
    """Remove placeholder emails - these should be updated by admin."""
    Customer = apps.get_model('customers', 'Customer')

    # Mark customers with default email
    Customer.objects.filter(
        email__in=['noemail@example.com', 'unknown@example.com']
    ).update(metadata={'needs_email_update': True})

class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_alter_customer_email'),
    ]

    operations = [
        migrations.RunPython(cleanup_default_emails),
    ]
```

#### Step 4: Apply Migrations

```powershell
python manage.py migrate_schemas
```

#### Step 5: Remove Default from Model

```python
# src/bookme/customers/models.py

class Customer(TenantAwareModel):
    name = models.CharField(max_length=200)
    email = models.EmailField()  # Clean - no default, no blank
    phone = models.CharField(max_length=20, blank=True)
```

---

## 🔄 Migration Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    1. EDIT MODELS                           │
│  src/bookme/<app>/models.py                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              2. CREATE MIGRATION FILES                      │
│  python manage.py makemigrations <app>                     │
│                                                             │
│  Creates: migrations/0002_<description>.py                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              3. REVIEW MIGRATION FILE                       │
│  Check: migrations/0002_<description>.py                   │
│  Verify: Operations are correct                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         4. TEST IN DEVELOPMENT (Optional but Recommended)   │
│  python manage.py migrate_schemas --schema=tenant_test     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            5. APPLY TO ALL TENANTS                          │
│  python manage.py migrate_schemas                          │
│                                                             │
│  This runs on:                                             │
│  - public schema (if shared app)                           │
│  - tenant_demo schema                                      │
│  - tenant_acme schema                                      │
│  - tenant_xyz schema                                       │
│  - ... all other tenant schemas                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 6. VERIFY                                   │
│  python manage.py showmigrations <app>                     │
│  Check: All migrations applied with [X]                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              7. COMMIT TO GIT                               │
│  git add src/bookme/<app>/migrations/                      │
│  git commit -m "Add <feature> to <model>"                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Common Scenarios & Solutions

### Scenario 1: Adding a Required Field

**Problem**: Can't add non-nullable field without default.

**Solution**: Provide a default value or make it nullable initially.

```python
# Option A: Provide default
field = models.CharField(max_length=100, default='default_value')

# Option B: Make nullable, fill data, then make required
# Step 1:
field = models.CharField(max_length=100, null=True, blank=True)
# Migrate, fill data with real values
# Step 2:
field = models.CharField(max_length=100)  # Remove null=True
```

### Scenario 2: Renaming a Field

```powershell
# Use RenameField operation
python manage.py makemigrations
```

Django detects renames automatically. If it asks:
```
Did you rename customer.phone_number to customer.phone? [y/N]: y
```

### Scenario 3: Deleting a Field

**⚠️ Warning**: This permanently deletes data!

```python
# Remove from model
class Customer(TenantAwareModel):
    name = models.CharField(max_length=200)
    # phone = models.CharField(max_length=20)  # REMOVED
```

```powershell
python manage.py makemigrations customers
# Confirms: Remove field phone from customer

# Back up data first!
python manage.py dumpdata customers > backup.json

# Then apply
python manage.py migrate_schemas
```

### Scenario 4: Migration Failed Mid-Way

**Problem**: Migration failed on tenant_xyz, but succeeded on others.

**Solution**: Fix the issue and re-run for that tenant only.

```powershell
# Check which migrations failed
python manage.py migrate_schemas --schema=tenant_xyz --list

# Fix the issue (e.g., bad data)

# Re-run for specific tenant
python manage.py migrate_schemas --schema=tenant_xyz

# Or rollback if needed
python manage.py migrate_schemas --schema=tenant_xyz <app> <migration_number>
```

---

## 🛡️ Safety Checklist

Before applying migrations to production:

- [ ] ✅ Tested migration in development environment
- [ ] ✅ Reviewed migration file for correctness
- [ ] ✅ Backed up database (production)
- [ ] ✅ Verified no data loss operations (unless intended)
- [ ] ✅ Tested rollback procedure (if possible)
- [ ] ✅ Scheduled during low-traffic period
- [ ] ✅ Have rollback plan ready
- [ ] ✅ Team members notified

---

## 📊 Checking Migration Status

### View All Migrations

```powershell
python manage.py showmigrations
```

**Output**:
```
services
 [X] 0001_initial
 [X] 0002_service_capacity
 [ ] 0003_servicecategory_service_category

customers
 [X] 0001_initial
 [X] 0002_customer_email_required
```

`[X]` = Applied
`[ ]` = Pending

### View Specific App

```powershell
python manage.py showmigrations services
```

### View for Specific Tenant

```powershell
python manage.py migrate_schemas --schema=tenant_demo --list
```

---

## 🔙 Rolling Back Migrations

### Rollback Last Migration

```powershell
# Rollback services app to previous migration
python manage.py migrate_schemas services 0001

# This undoes migration 0002
```

### Rollback to Specific Migration

```powershell
# Rollback to specific migration number
python manage.py migrate_schemas services 0002

# This undoes all migrations after 0002
```

### Rollback for Specific Tenant

```powershell
python manage.py migrate_schemas --schema=tenant_demo services 0001
```

---

## 🧪 Testing Migrations

### Test on Specific Tenant First

```powershell
# Create test tenant if needed
python manage.py shell
```

```python
from bookme.tenant.models import Tenant, Domain

test_tenant = Tenant.objects.create(
    schema_name='tenant_test',
    name='Test Tenant',
    primary_domain='test.localhost',
    contact_email='test@test.com',
    status='active'
)

Domain.objects.create(
    domain='test.localhost',
    tenant=test_tenant,
    is_primary=True
)
```

```powershell
# Run migration on test tenant only
python manage.py migrate_schemas --schema=tenant_test

# Verify it worked
python manage.py shell
```

```python
from django.db import connection
from bookme.tenant.models import Tenant
from bookme.services.models import Service

tenant = Tenant.objects.get(schema_name='tenant_test')
connection.set_tenant(tenant)

# Test the new field
service = Service.objects.first()
print(service.capacity)  # Should work!
```

---

## 📝 Migration Best Practices

### 1. Small, Focused Migrations
✅ **Good**: One logical change per migration
```
0002_add_capacity_to_service.py
0003_add_service_category.py
```

❌ **Bad**: Multiple unrelated changes
```
0002_add_everything.py  # capacity, category, refactor, etc.
```

### 2. Meaningful Names
```powershell
# Use descriptive names
python manage.py makemigrations services --name add_capacity_field

# Creates: 0002_add_capacity_field.py
```

### 3. Always Provide Defaults
```python
# For new non-nullable fields
capacity = models.PositiveIntegerField(default=1)
```

### 4. Test Before Applying to All
```powershell
# Test on one tenant first
python manage.py migrate_schemas --schema=tenant_test
```

### 5. Back Up Production Data
```powershell
# Before major migrations
docker exec bookme_db pg_dump -U bookme bookme > backup_$(date +%Y%m%d).sql
```

---

## 🆘 Troubleshooting

### Error: "relation already exists"

**Cause**: Migration was partially applied.

**Solution**: Fake the migration, then fix data manually.

```powershell
python manage.py migrate_schemas --fake services 0002
```

### Error: "column does not exist"

**Cause**: Migration order is wrong.

**Solution**: Check dependencies in migration file.

```python
# In migration file
class Migration(migrations.Migration):
    dependencies = [
        ('services', '0001_initial'),  # Make sure this is correct
    ]
```

### Error: "cannot ALTER TABLE in tenant schema"

**Cause**: Trying to modify shared app from tenant context.

**Solution**: Shared apps must be migrated with `--shared` flag.

```powershell
python manage.py migrate_schemas --shared
```

---

## 📚 Additional Resources

- [Django Migrations Documentation](https://docs.djangoproject.com/en/5.0/topics/migrations/)
- [Django-Tenants Migrations](https://django-tenants.readthedocs.io/en/latest/use.html#migrations)
- [Full Tenant Guide](TENANT_GUIDE.md)
- [Quick Reference](CHEAT_SHEET.md)

---

**Need Help?** Check [TENANT_GUIDE.md](TENANT_GUIDE.md) or ask the team! 🚀
