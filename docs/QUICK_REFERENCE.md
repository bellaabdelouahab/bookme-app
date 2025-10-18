# Multi-Tenant Quick Reference Card

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    BOOKME.MA PLATFORM                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐         ┌────────────┐                 │
│  │  Client    │────────▶│   Nginx    │                 │
│  │  Browser   │         │  (Proxy)   │                 │
│  └────────────┘         └─────┬──────┘                 │
│                               │                         │
│                               ▼                         │
│                    ┌──────────────────┐                │
│                    │   Django App     │                │
│                    │   + Middleware   │                │
│                    └────────┬─────────┘                │
│                             │                           │
│              ┌──────────────┼──────────────┐           │
│              │              │              │           │
│              ▼              ▼              ▼           │
│      ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│      │ Public   │   │ Tenant A │   │ Tenant B │      │
│      │ Schema   │   │ Schema   │   │ Schema   │      │
│      │          │   │          │   │          │      │
│      │ Users    │   │ Services │   │ Services │      │
│      │ Tenants  │   │ Bookings │   │ Bookings │      │
│      │ Domains  │   │ Customers│   │ Customers│      │
│      └──────────┘   └──────────┘   └──────────┘      │
│                                                          │
│            PostgreSQL Database (Single Instance)         │
└──────────────────────────────────────────────────────────┘
```

## 📊 Schema Organization

### Public Schema (Shared)
- `users_user` - User accounts
- `users_tenant_membership` - User-tenant relationships
- `tenant_tenant` - Tenant definitions
- `tenant_domain` - Domain routing
- `tenant_config` - Tenant settings
- `tenant_lifecycle` - Audit logs

### Tenant Schema (Isolated)
- `services_service` - Services
- `services_category` - Categories
- `staff_staff` - Staff members
- `staff_availability` - Schedules
- `customers_customer` - Customers
- `bookings_booking` - Bookings
- `bookings_booking_event` - Events
- `communications_*` - Notifications
- `payments_transaction` - Payments
- `resources_resource` - Resources

## 🔧 Essential Commands

### Setup
```bash
# Install
pip install -e ".[dev]"

# Start services
docker-compose up -d db redis

# Migrate
python manage.py migrate_schemas --shared
python manage.py migrate_schemas

# Create admin
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Development
```bash
# Django shell
python manage.py shell

# Make migrations
python manage.py makemigrations [app]

# Apply migrations
python manage.py migrate_schemas

# Run tests
pytest

# Format code
black .

# Lint
ruff check .
```

### Tenant Management
```python
# Create tenant (in shell)
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

## 🎨 Model Template

```python
from bookme.core.models import TenantAwareModel
from django.db import models

class MyModel(TenantAwareModel):
    """Model description."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "app_mymodel"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name", "is_active"]),
        ]

    def __str__(self):
        return self.name
```

## 🔐 API Patterns

### ViewSet
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering = ['-created_at']
```

### Serializer
```python
from rest_framework import serializers

class MySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'description',
                  'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
```

## 🧪 Test Template

```python
from django_tenants.test.cases import TenantTestCase

class MyTest(TenantTestCase):

    def test_something(self):
        obj = MyModel.objects.create(name='Test')
        self.assertEqual(obj.name, 'Test')
```

## ⚠️ Common Mistakes

| ❌ Don't | ✅ Do |
|---------|------|
| `python manage.py migrate` | `python manage.py migrate_schemas` |
| `ForeignKey(User)` in tenant model | `UUIDField()` reference |
| Create tenant without domain | Always create domain |
| Forget `is_primary=True` | Set primary domain |

## 🔍 Quick Debugging

```python
# Check current schema
from django.db import connection
print(connection.schema_name)

# Switch tenant
tenant = Tenant.objects.get(schema_name='tenant_demo')
connection.set_tenant(tenant)

# List all schemas
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    """)
    for row in cursor.fetchall():
        print(row[0])
```

## 📝 Migration Workflow

```
Edit Model → makemigrations → Review → migrate_schemas
```

```bash
# 1. Edit model
# src/bookme/app/models.py

# 2. Create migration
python manage.py makemigrations app

# 3. Review
# Check migrations/0002_xxx.py

# 4. Apply to all tenants
python manage.py migrate_schemas

# 5. Verify
python manage.py showmigrations app
```

## 🌐 URLs

### Development
- Public: `http://localhost:8000`
- Tenant: `http://{tenant}.localhost:8000`
- Admin: `http://localhost:8000/admin`
- API: `http://localhost:8000/api/`
- Docs: `http://localhost:8000/api/schema/swagger/`

### Hosts File
```
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/Mac: /etc/hosts
127.0.0.1  localhost
127.0.0.1  demo.localhost
127.0.0.1  test.localhost
```

## 📚 Documentation

- **TENANT_GUIDE.md** - Complete multi-tenant guide
- **CHEAT_SHEET.md** - Quick reference
- **MIGRATION_GUIDE.md** - Database updates
- **COMMON_TASKS.md** - Practical examples

## 🎯 Key Concepts

**Tenant**: A single business/organization
**Schema**: PostgreSQL database schema (like a namespace)
**Domain**: URL used to access a tenant
**Shared Apps**: Data in public schema (all tenants)
**Tenant Apps**: Data in tenant schemas (isolated)

**Routing**: `demo.localhost` → Middleware → `tenant_demo` schema

## 💡 Tips

1. Always use `migrate_schemas` not `migrate`
2. Inherit from `TenantAwareModel` for tenant models
3. Don't FK between shared and tenant models
4. Always create domain when creating tenant
5. Use `connection.set_tenant()` for cross-tenant queries
6. Test migrations on one tenant first
7. Keep [CHEAT_SHEET.md](CHEAT_SHEET.md) open while coding

---

**Version**: 1.0 | **Updated**: October 2025
**Full Docs**: `docs/README.md` | **Project**: BookMe.ma
