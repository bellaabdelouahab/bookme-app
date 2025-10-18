# Multi-Tenant Development Cheat Sheet

## 🚀 Quick Start (New Developer)

```powershell
# 1. Clone and setup
git clone <repo-url>
cd bookme.ma
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Edit .env if needed

# 3. Start database
docker-compose up -d db redis

# 4. Setup database
cd src
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
python manage.py createsuperuser

# 5. Create test tenant
python manage.py shell
```

```python
from bookme.tenant.models import Tenant, Domain

tenant = Tenant.objects.create(
    schema_name='tenant_demo',
    name='Demo Company',
    primary_domain='demo.localhost',
    contact_email='demo@test.com',
    status='active'
)

Domain.objects.create(
    domain='demo.localhost',
    tenant=tenant,
    is_primary=True
)
```

```powershell
# 6. Run server
python manage.py runserver

# Access: http://demo.localhost:8000
```

---

## 📊 Database Structure

### Shared Schema (Public)
```
public/
├── users_user                    # User accounts
├── users_tenant_membership       # User-Tenant relationships
├── tenant_tenant                 # Tenant definitions
├── tenant_domain                 # Domain routing
├── tenant_config                 # Tenant settings
└── tenant_lifecycle              # Audit logs
```

### Tenant Schema (Per Tenant)
```
tenant_demo/
├── services_service              # Services catalog
├── staff_staff                   # Staff members
├── staff_availability            # Staff schedules
├── customers_customer            # Customers
├── bookings_booking              # Bookings
├── bookings_booking_event        # Booking events
├── communications_*              # Notifications
├── payments_transaction          # Payments
└── resources_resource            # Resources
```

---

## 🔧 Common Tasks

### Add a New Field to Existing Model

```python
# 1. Edit model (e.g., bookme/services/models.py)
class Service(TenantAwareModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)  # NEW
```

```powershell
# 2. Create migration
python manage.py makemigrations services

# 3. Apply to all tenants
python manage.py migrate_schemas

# Done! Field added to all tenant schemas
```

### Create a New Model

```python
# 1. Add to appropriate app (e.g., bookme/services/models.py)
from bookme.core.models import TenantAwareModel

class ServiceCategory(TenantAwareModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "services_category"
        verbose_name_plural = "Service Categories"
```

```powershell
# 2. Create migration
python manage.py makemigrations services

# 3. Apply migration
python manage.py migrate_schemas
```

### Create New Tenant

```python
# In Django shell (python manage.py shell)
from bookme.tenant.models import Tenant, Domain

# Create tenant
tenant = Tenant.objects.create(
    schema_name='tenant_acme',      # Unique, lowercase
    name='Acme Corporation',
    primary_domain='acme.bookme.ma',
    contact_email='admin@acme.com',
    status='active'
)

# Create domain
Domain.objects.create(
    domain='acme.bookme.ma',
    tenant=tenant,
    is_primary=True
)

# Optional: Add localhost domain for development
Domain.objects.create(
    domain='acme.localhost',
    tenant=tenant,
    is_primary=False
)
```

### Query Data in Specific Tenant

```python
# Method 1: Via domain (automatic)
# Just access via tenant's domain: http://demo.localhost:8000
# All queries automatically scoped to that tenant

# Method 2: Programmatically switch tenant
from django.db import connection
from bookme.tenant.models import Tenant
from bookme.services.models import Service

# Get tenant
tenant = Tenant.objects.get(schema_name='tenant_demo')

# Switch to tenant
connection.set_tenant(tenant)

# Query data (now scoped to tenant_demo)
services = Service.objects.all()
print(f"Tenant has {services.count()} services")

# Switch back to public
connection.set_schema_to_public()
```

### List All Tenants and Their Data

```python
from django.db import connection
from bookme.tenant.models import Tenant
from bookme.bookings.models import Booking

for tenant in Tenant.objects.all():
    connection.set_tenant(tenant)

    booking_count = Booking.objects.count()

    print(f"📊 {tenant.name}")
    print(f"   Schema: {tenant.schema_name}")
    print(f"   Status: {tenant.status}")
    print(f"   Bookings: {booking_count}")
    print()

connection.set_schema_to_public()
```

---

## 🧪 Testing

### Write a Test

```python
# tests/test_services.py
from django_tenants.test.cases import TenantTestCase
from bookme.tenant.models import Tenant, Domain
from bookme.services.models import Service

class ServiceTest(TenantTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tenant = Tenant.objects.create(
            schema_name='test',
            name='Test Tenant',
            primary_domain='test.localhost',
            contact_email='test@test.com'
        )
        Domain.objects.create(
            domain='test.localhost',
            tenant=cls.tenant,
            is_primary=True
        )

    def test_create_service(self):
        service = Service.objects.create(
            name='Test Service',
            price=50.00
        )
        self.assertEqual(service.name, 'Test Service')
```

```powershell
# Run tests
pytest tests/test_services.py -v
```

---

## ⚠️ Common Mistakes

### ❌ Using Regular migrate
```powershell
python manage.py migrate  # Only migrates public schema!
```

### ✅ Use migrate_schemas
```powershell
python manage.py migrate_schemas  # Migrates ALL schemas
```

---

### ❌ Direct ForeignKey Between Shared and Tenant Models
```python
# bookme/bookings/models.py
class Booking(TenantAwareModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ❌ Cross-schema FK!
```

### ✅ Store UUID Reference
```python
class Booking(TenantAwareModel):
    user_id = models.UUIDField()  # ✅ Store UUID
    user_email = models.EmailField()  # ✅ Denormalize important fields
```

---

### ❌ Forgetting to Create Domain
```python
tenant = Tenant.objects.create(...)  # ❌ Can't access tenant!
```

### ✅ Always Create Domain
```python
tenant = Tenant.objects.create(...)
Domain.objects.create(domain='demo.localhost', tenant=tenant, is_primary=True)
```

---

## 🔍 Debugging Tips

### Check Current Tenant
```python
from django.db import connection

# Get current schema
print(f"Current schema: {connection.schema_name}")

# Get current tenant
print(f"Current tenant: {connection.tenant}")
```

### Verify Tenant Schema Exists
```python
from bookme.tenant.models import Tenant

tenant = Tenant.objects.get(schema_name='tenant_demo')
print(f"Schema exists: {tenant.schema_name}")
print(f"Auto create: {tenant.auto_create_schema}")
```

### List All Schemas in Database
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    """)
    schemas = cursor.fetchall()

for schema in schemas:
    print(f"📁 {schema[0]}")
```

### Check Migration Status
```powershell
# Show all migrations
python manage.py showmigrations

# Show migrations for specific app
python manage.py showmigrations services

# Show migrations for specific tenant
python manage.py migrate_schemas --schema=tenant_demo --list
```

---

## 📝 Model Templates

### Tenant-Aware Model Template
```python
from bookme.core.models import TenantAwareModel
from django.db import models

class MyModel(TenantAwareModel):
    """Model description."""

    # Fields
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Relations (only to models in same schema!)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    # Metadata inherited from TenantAwareModel:
    # - id (UUID)
    # - created_at
    # - updated_at
    # - metadata (JSONField)

    class Meta:
        db_table = "app_mymodel"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name", "is_active"]),
        ]

    def __str__(self):
        return self.name
```

### Admin Template
```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"
```

### Serializer Template
```python
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
```

### ViewSet Template
```python
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]
```

---

## 🔗 Useful URLs

### Development
- Public: http://localhost:8000
- Admin: http://localhost:8000/admin
- API: http://localhost:8000/api/
- API Docs: http://localhost:8000/api/schema/swagger/

### Tenant-Specific (replace `demo` with tenant domain)
- Tenant: http://demo.localhost:8000
- Tenant Admin: http://demo.localhost:8000/admin
- Tenant API: http://demo.localhost:8000/api/

---

## 📚 Related Documentation

- [Full Tenant Guide](TENANT_GUIDE.md) - Comprehensive guide
- [Setup Guide](SETUP_GUIDE.md) - Installation instructions
- [Architecture](architecture/modular-monolith.md) - System design
- [README](../README.md) - Project overview

---

## 🆘 Quick Help

| Problem | Solution |
|---------|----------|
| Can't access tenant URL | Check domain is created and hosts file configured |
| Migrations fail | Use `migrate_schemas` not `migrate` |
| Data appears in wrong tenant | Check middleware is installed correctly |
| Can't query across schemas | Use `connection.set_tenant()` to switch |
| ForeignKey error | Don't link shared and tenant models directly |
| Test fails with schema error | Use `TenantTestCase` not `TestCase` |

---

**Last Updated**: October 2025
**Questions?** Ask the team or check [TENANT_GUIDE.md](TENANT_GUIDE.md) for details!
