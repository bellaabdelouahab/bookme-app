# Multi-Tenant Architecture Guide

## Table of Contents
1. [What is Multi-Tenancy?](#what-is-multi-tenancy)
2. [How Our System Works](#how-our-system-works)
3. [Database Schema Isolation](#database-schema-isolation)
4. [Development Workflow](#development-workflow)
5. [Working with Models](#working-with-models)
6. [Database Migrations](#database-migrations)
7. [Creating and Managing Tenants](#creating-and-managing-tenants)
8. [Testing Multi-Tenant Features](#testing-multi-tenant-features)
9. [Common Pitfalls](#common-pitfalls)

---

## What is Multi-Tenancy?

**Multi-tenancy** is an architecture where a single application serves multiple customers (tenants), while keeping their data completely isolated from each other.

### Real-World Analogy
Think of an apartment building:
- 🏢 **The Building** = Our Django Application
- 🚪 **Each Apartment** = A Tenant (Business/Company)
- 🔑 **Apartment Key** = Domain/Subdomain
- 📦 **Personal Items** = Tenant's Data (customers, bookings, etc.)

Just like apartments share the same building structure but have separate living spaces, tenants share the same application but have isolated data.

### Why Multi-Tenancy?

✅ **Benefits:**
- One codebase serves thousands of businesses
- Efficient resource usage
- Easy updates (deploy once, affects all tenants)
- Lower hosting costs per customer

❌ **Without Multi-Tenancy:**
- Need separate deployment per customer
- Difficult to maintain updates
- Higher infrastructure costs

---

## How Our System Works

We use **Schema-based isolation** with `django-tenants`:

```
┌─────────────────────────────────────────┐
│         PostgreSQL Database             │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    PUBLIC SCHEMA     │
│  │ Users        │    (Shared Data)      │
│  │ Tenants      │                       │
│  │ Domains      │                       │
│  └──────────────┘                       │
│                                         │
│  ┌──────────────┐    tenant_acme       │
│  │ Services     │    (Acme Corp Data)   │
│  │ Bookings     │                       │
│  │ Customers    │                       │
│  └──────────────┘                       │
│                                         │
│  ┌──────────────┐    tenant_xyz        │
│  │ Services     │    (XYZ Inc Data)     │
│  │ Bookings     │                       │
│  │ Customers    │                       │
│  └──────────────┘                       │
│                                         │
└─────────────────────────────────────────┘
```

### How Routing Works

1. **User visits**: `acme.bookme.ma`
2. **Middleware checks**: Which tenant owns this domain?
3. **Database switches**: Sets `search_path=tenant_acme`
4. **All queries**: Automatically scoped to Acme's schema

```python
# You write this:
services = Service.objects.all()

# Django-tenants automatically makes it:
# SELECT * FROM tenant_acme.services_service
# (instead of public.services_service)
```

---

## Database Schema Isolation

### Shared Apps (Public Schema)
Data that is **shared across all tenants**:

```python
SHARED_APPS = [
    "django_tenants",
    "django.contrib.auth",
    "django.contrib.sessions",
    "bookme.users",        # Users can belong to multiple tenants
    "bookme.tenant",       # Tenant management
]
```

**Stored in**: `public` schema
**Examples**: User accounts, tenant definitions, domains

### Tenant Apps (Tenant Schemas)
Data that is **isolated per tenant**:

```python
TENANT_APPS = [
    "bookme.services",      # Each tenant has their own services
    "bookme.staff",         # Each tenant has their own staff
    "bookme.customers",     # Customers are tenant-specific
    "bookme.bookings",      # Bookings belong to one tenant
    "bookme.communications",
    "bookme.payments",
    "bookme.resources",
]
```

**Stored in**: `tenant_{id}` schemas
**Examples**: Services, bookings, customers, payments

---

## Development Workflow

### 1. Initial Setup

```powershell
# Clone the repository
git clone <repo-url>
cd bookme.ma

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start database services
docker-compose up -d db redis

# Run migrations
cd src
python manage.py migrate_schemas --shared    # Shared schema
python manage.py migrate_schemas             # All tenant schemas
```

### 2. Creating Your First Tenant

```powershell
# Create superuser first
python manage.py createsuperuser

# Create a tenant using Django shell
python manage.py shell
```

```python
from bookme.tenant.models import Tenant, Domain

# Create tenant
tenant = Tenant.objects.create(
    schema_name='tenant_demo',
    name='Demo Company',
    primary_domain='demo.localhost',
    contact_email='admin@demo.com',
    status='active'
)

# Create domain for routing
domain = Domain.objects.create(
    domain='demo.localhost',
    tenant=tenant,
    is_primary=True
)

print(f"✅ Tenant created: {tenant.name}")
print(f"   Access at: http://demo.localhost:8000")
```

### 3. Running the Development Server

```powershell
# Start the server
python manage.py runserver

# Access tenants:
# - Public site: http://localhost:8000
# - Demo tenant: http://demo.localhost:8000
# - Another tenant: http://acme.localhost:8000
```

---

## Working with Models

### Creating Tenant-Aware Models

All tenant-specific models should inherit from `TenantAwareModel`:

```python
# ❌ DON'T: Regular Django model
from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)


# ✅ DO: Tenant-aware model
from bookme.core.models import TenantAwareModel

class Service(TenantAwareModel):  # Inherits id, created_at, updated_at, metadata
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "services_service"
        ordering = ["-created_at"]
```

**Benefits of TenantAwareModel:**
- ✅ UUID primary keys (better for distributed systems)
- ✅ Automatic timestamps (`created_at`, `updated_at`)
- ✅ JSON metadata field (extensibility without migrations)
- ✅ Consistent structure across all models

### Querying Data

```python
# No special code needed! Django-tenants handles everything:

# This automatically queries the current tenant's schema
services = Service.objects.all()
bookings = Booking.objects.filter(status='confirmed')

# The middleware sets the correct schema based on the domain:
# - If accessed via demo.localhost → queries tenant_demo.services_service
# - If accessed via acme.localhost → queries tenant_acme.services_service
```

### Cross-Tenant Queries (Rare)

Sometimes you need to query across tenants (admin dashboards, analytics):

```python
from django.db import connection
from bookme.tenant.models import Tenant

# Get all tenants
tenants = Tenant.objects.all()

results = []
for tenant in tenants:
    connection.set_tenant(tenant)  # Switch to tenant's schema

    # Now queries are scoped to this tenant
    booking_count = Booking.objects.count()
    results.append({
        'tenant': tenant.name,
        'bookings': booking_count
    })

# Reset to public schema
connection.set_schema_to_public()
```

---

## Database Migrations

### Understanding Migration Types

**Shared Migrations** (run once on public schema):
- User model changes
- Tenant model changes
- Core/shared app changes

**Tenant Migrations** (run on each tenant schema):
- Service model changes
- Booking model changes
- Any tenant-specific app changes

### Creating Migrations

```powershell
# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations services

# Create migration for specific model
python manage.py makemigrations services --name add_duration_field
```

### Running Migrations

```powershell
# Option 1: Run all migrations (recommended)
python manage.py migrate_schemas

# Option 2: Run only shared schema migrations
python manage.py migrate_schemas --shared

# Option 3: Run migrations for specific tenant
python manage.py migrate_schemas --schema=tenant_demo

# Option 4: Run migrations for all tenants except public
python manage.py migrate_schemas --executor=parallel  # Faster for many tenants
```

### Migration Workflow Example

**Scenario**: Add a `duration_minutes` field to Service model

1. **Edit the model**:
```python
# bookme/services/models.py
class Service(TenantAwareModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(default=60)  # NEW FIELD
```

2. **Create migration**:
```powershell
python manage.py makemigrations services
# Creates: services/migrations/0002_service_duration_minutes.py
```

3. **Review migration file**:
```python
# services/migrations/0002_service_duration_minutes.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='duration_minutes',
            field=models.IntegerField(default=60),
        ),
    ]
```

4. **Run migration**:
```powershell
python manage.py migrate_schemas
```

5. **Output**:
```
[standard:tenant_demo] === Running migrations
[standard:tenant_demo]   Applying services.0002_service_duration_minutes... OK
[standard:tenant_acme] === Running migrations
[standard:tenant_acme]   Applying services.0002_service_duration_minutes... OK
[standard:tenant_xyz] === Running migrations
[standard:tenant_xyz]   Applying services.0002_service_duration_minutes... OK
```

✅ **Result**: All tenants now have the `duration_minutes` field!

---

## Creating and Managing Tenants

### Method 1: Django Shell

```powershell
python manage.py shell
```

```python
from bookme.tenant.models import Tenant, Domain

# Create tenant
tenant = Tenant.objects.create(
    schema_name='tenant_acmecorp',  # Must be unique, lowercase, no spaces
    name='Acme Corporation',
    primary_domain='acme.bookme.ma',
    contact_email='admin@acme.com',
    contact_phone='+1234567890',
    status='active',
    subscription_tier='premium',
    max_staff=20,
    max_services=50,
    metadata={
        'industry': 'healthcare',
        'timezone': 'America/New_York'
    }
)

# Create primary domain
domain = Domain.objects.create(
    domain='acme.bookme.ma',
    tenant=tenant,
    is_primary=True
)

# Create additional domains (optional)
Domain.objects.create(
    domain='acme.localhost',  # For local development
    tenant=tenant,
    is_primary=False
)

print(f"✅ Tenant '{tenant.name}' created successfully!")
print(f"   Schema: {tenant.schema_name}")
print(f"   Domain: {domain.domain}")
```

### Method 2: Management Command (Create One)

```python
# bookme/tenant/management/commands/create_tenant.py
from django.core.management.base import BaseCommand
from bookme.tenant.models import Tenant, Domain

class Command(BaseCommand):
    help = 'Create a new tenant'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('domain', type=str)
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        schema_name = f"tenant_{options['name'].lower().replace(' ', '_')}"

        tenant = Tenant.objects.create(
            schema_name=schema_name,
            name=options['name'],
            primary_domain=options['domain'],
            contact_email=options['email'],
            status='active'
        )

        Domain.objects.create(
            domain=options['domain'],
            tenant=tenant,
            is_primary=True
        )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Tenant '{tenant.name}' created at {options['domain']}"
        ))
```

**Usage**:
```powershell
python manage.py create_tenant "Acme Corp" "acme.bookme.ma" "admin@acme.com"
```

### Method 3: API Endpoint (Production)

```python
# bookme/tenant/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tenant, Domain
from .serializers import TenantSerializer

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    @action(detail=False, methods=['post'])
    def create_with_domain(self, request):
        """Create tenant with automatic domain setup"""
        name = request.data.get('name')
        domain = request.data.get('domain')
        email = request.data.get('email')

        # Create tenant
        tenant = Tenant.objects.create(
            schema_name=f"tenant_{name.lower().replace(' ', '_')}",
            name=name,
            primary_domain=domain,
            contact_email=email,
            status='trial'  # Start with trial
        )

        # Create domain
        Domain.objects.create(
            domain=domain,
            tenant=tenant,
            is_primary=True
        )

        # Run migrations for new tenant
        from django.core.management import call_command
        call_command('migrate_schemas', schema_name=tenant.schema_name)

        return Response({
            'tenant_id': str(tenant.id),
            'schema_name': tenant.schema_name,
            'domain': domain,
            'status': 'created'
        }, status=status.HTTP_201_CREATED)
```

### Listing Tenants

```python
# In Django shell
from bookme.tenant.models import Tenant

# All tenants
for tenant in Tenant.objects.all():
    print(f"📊 {tenant.name}")
    print(f"   Schema: {tenant.schema_name}")
    print(f"   Status: {tenant.status}")
    print(f"   Domains: {', '.join([d.domain for d in tenant.domains.all()])}")
    print()
```

### Deleting a Tenant

```python
# ⚠️ DANGER: This deletes ALL tenant data!

from bookme.tenant.models import Tenant

tenant = Tenant.objects.get(schema_name='tenant_demo')

# This will:
# 1. Delete all data in tenant_demo schema
# 2. Drop the schema
# 3. Remove tenant and domain records
tenant.delete(force_drop=True)

print("✅ Tenant deleted")
```

---

## Testing Multi-Tenant Features

### Unit Tests with Tenant Context

```python
# tests/test_services.py
from django.test import TestCase
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from bookme.tenant.models import Tenant, Domain
from bookme.services.models import Service

class ServiceTestCase(TenantTestCase):
    """Tests that run within a tenant context"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test tenant
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
        """Test creating a service in tenant schema"""
        service = Service.objects.create(
            name='Haircut',
            price=50.00,
            duration_minutes=30
        )

        self.assertEqual(service.name, 'Haircut')
        self.assertEqual(Service.objects.count(), 1)

    def test_service_isolation(self):
        """Test that services are isolated per tenant"""
        Service.objects.create(name='Service 1', price=10)

        # Create another tenant
        tenant2 = Tenant.objects.create(
            schema_name='test2',
            name='Test Tenant 2',
            primary_domain='test2.localhost',
            contact_email='test2@test.com'
        )

        # Switch to tenant2
        from django.db import connection
        connection.set_tenant(tenant2)

        # Should be empty in tenant2
        self.assertEqual(Service.objects.count(), 0)

        # Switch back
        connection.set_tenant(self.tenant)
        self.assertEqual(Service.objects.count(), 1)
```

### API Tests

```python
# tests/test_api.py
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework.test import APIClient

class BookingAPITestCase(TenantTestCase):

    def setUp(self):
        super().setUp()
        self.client = TenantClient(self.tenant)

    def test_create_booking(self):
        """Test creating a booking via API"""
        response = self.client.post('/api/bookings/', {
            'service_id': str(self.service.id),
            'customer_email': 'customer@example.com',
            'start_time': '2025-10-20T10:00:00Z'
        })

        self.assertEqual(response.status_code, 201)
```

### Running Tests

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_services.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests for specific app
pytest tests/test_services.py -v
```

---

## Common Pitfalls

### 1. ❌ Forgetting to Use migrate_schemas

```powershell
# DON'T do this:
python manage.py migrate  # Only migrates public schema!

# DO this:
python manage.py migrate_schemas  # Migrates all schemas
```

### 2. ❌ Hardcoding Schema Names

```python
# DON'T:
Service.objects.raw("SELECT * FROM tenant_acme.services_service")

# DO:
Service.objects.all()  # Django-tenants handles schema routing
```

### 3. ❌ Mixing Shared and Tenant Models

```python
# DON'T: Trying to relate tenant model to shared model directly
class Booking(TenantAwareModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ❌ User is in public schema!

# DO: Use UUIDs and store references
class Booking(TenantAwareModel):
    user_id = models.UUIDField()  # ✅ Store UUID reference
    user_email = models.EmailField()  # ✅ Denormalize when needed
```

### 4. ❌ Not Setting Primary Domain

```python
# DON'T: Create tenant without domain
tenant = Tenant.objects.create(...)  # Can't access it!

# DO: Always create domain
tenant = Tenant.objects.create(...)
Domain.objects.create(domain='example.com', tenant=tenant, is_primary=True)
```

### 5. ❌ Using localhost Without Proper Setup

For local development with subdomains, add to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
127.0.0.1  localhost
127.0.0.1  demo.localhost
127.0.0.1  acme.localhost
127.0.0.1  test.localhost
```

### 6. ❌ Not Handling Tenant Context in Celery Tasks

```python
# DON'T: Task without tenant context
@shared_task
def send_booking_confirmation(booking_id):
    booking = Booking.objects.get(id=booking_id)  # ❌ Which tenant?

# DO: Pass tenant schema
@shared_task
def send_booking_confirmation(booking_id, schema_name):
    from django.db import connection
    from bookme.tenant.models import Tenant

    tenant = Tenant.objects.get(schema_name=schema_name)
    connection.set_tenant(tenant)

    booking = Booking.objects.get(id=booking_id)  # ✅ Correct tenant
    # Send email...
```

---

## Quick Reference Commands

```powershell
# Development
python manage.py runserver                  # Start development server
python manage.py shell                      # Django shell
python manage.py createsuperuser           # Create admin user

# Migrations
python manage.py makemigrations            # Create migrations
python manage.py migrate_schemas           # Run all migrations
python manage.py migrate_schemas --shared  # Run shared only
python manage.py showmigrations            # Show migration status

# Tenant Management
python manage.py shell                     # Use for creating tenants
python manage.py tenant_command <schema>   # Run command for specific tenant

# Database
docker-compose up -d db redis             # Start services
docker-compose down                        # Stop services
docker-compose logs -f db                 # View database logs

# Testing
pytest                                     # Run tests
pytest --cov=src                          # Run with coverage
pytest -v -s                              # Verbose with print output

# Code Quality
black .                                   # Format code
ruff check .                              # Lint code
mypy src/                                 # Type checking
```

---

## Additional Resources

- 📚 [Django-Tenants Documentation](https://django-tenants.readthedocs.io/)
- 📚 [Django Documentation](https://docs.djangoproject.com/)
- 📚 [PostgreSQL Schemas](https://www.postgresql.org/docs/current/ddl-schemas.html)
- 📁 [Project README](../README.md)
- 📁 [Setup Guide](SETUP_GUIDE.md)
- 📁 [Architecture Overview](architecture/modular-monolith.md)

---

## Need Help?

**Common Questions:**
- ❓ "How do I add a new model?" → See [Working with Models](#working-with-models)
- ❓ "How do I update the database?" → See [Database Migrations](#database-migrations)
- ❓ "How do I create a new tenant?" → See [Creating and Managing Tenants](#creating-and-managing-tenants)
- ❓ "Why can't I access my tenant?" → Check domain is created and hosts file is configured
- ❓ "Migrations failing?" → Check if you're using `migrate_schemas` not `migrate`

**Still stuck?** Check existing code examples in the `bookme/` directory or ask the team! 🚀
