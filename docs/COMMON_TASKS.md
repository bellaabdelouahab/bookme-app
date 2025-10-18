# Common Development Tasks

Quick solutions for everyday development scenarios in the BookMe multi-tenant platform.

## 🏁 Getting Started (First Day)

### 1. Set Up Your Environment

```powershell
# Clone the repo
git clone <repo-url>
cd bookme.ma

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Start database
docker-compose up -d db redis

# Run migrations
cd src
python manage.py migrate_schemas --shared
python manage.py migrate_schemas

# Create admin account
python manage.py createsuperuser
```

### 2. Create Demo Tenant

```python
# python manage.py shell
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

print(f"✅ Tenant created! Access at: http://demo.localhost:8000")
```

### 3. Run Server

```powershell
python manage.py runserver
```

**You're ready!** 🎉

---

## 🆕 Adding a New Feature

### Task: Add "Notes" Field to Booking

#### 1. Update the Model

```python
# src/bookme/bookings/models.py

class Booking(TenantAwareModel):
    # ... existing fields ...

    # ADD THIS
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the booking"
    )
```

#### 2. Create Migration

```powershell
python manage.py makemigrations bookings
```

#### 3. Apply Migration

```powershell
python manage.py migrate_schemas
```

#### 4. Update Serializer (for API)

```python
# src/bookme/bookings/serializers.py

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id',
            'service',
            'customer',
            'start_time',
            'end_time',
            'status',
            'notes',  # ADD THIS
            'created_at',
            'updated_at',
        ]
```

#### 5. Update Admin (for Django Admin)

```python
# src/bookme/bookings/admin.py

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'service', 'customer', 'start_time', 'status']
    list_filter = ['status', 'start_time']
    search_fields = ['customer__name', 'service__name', 'notes']  # ADD notes
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = [
        ('Booking Information', {
            'fields': ['service', 'customer', 'start_time', 'end_time']
        }),
        ('Status', {
            'fields': ['status', 'notes']  # ADD notes
        }),
        ('Metadata', {
            'fields': ['id', 'created_at', 'updated_at', 'metadata'],
            'classes': ['collapse']
        }),
    ]
```

✅ **Done!** Restart server and test.

---

## 🎨 Creating a New Model

### Task: Add "ServicePackage" Model

#### 1. Define the Model

```python
# src/bookme/services/models.py

class ServicePackage(TenantAwareModel):
    """A package/bundle of multiple services at a discounted price."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    services = models.ManyToManyField(Service, related_name='packages')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    package_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True, db_index=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "services_package"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "valid_from", "valid_until"]),
        ]

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.original_price > 0:
            discount = self.original_price - self.package_price
            return (discount / self.original_price) * 100
        return 0
```

#### 2. Create Serializer

```python
# src/bookme/services/serializers.py

from rest_framework import serializers
from .models import Service, ServicePackage

class ServicePackageSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Service.objects.all()
    )
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = ServicePackage
        fields = [
            'id',
            'name',
            'description',
            'services',
            'original_price',
            'package_price',
            'discount_percentage',
            'is_active',
            'valid_from',
            'valid_until',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

#### 3. Create ViewSet

```python
# src/bookme/services/views.py

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Service, ServicePackage
from .serializers import ServiceSerializer, ServicePackageSerializer

class ServicePackageViewSet(viewsets.ModelViewSet):
    queryset = ServicePackage.objects.all()
    serializer_class = ServicePackageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'package_price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter active packages or all for staff."""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Only show active packages to regular users
            queryset = queryset.filter(is_active=True)
        return queryset
```

#### 4. Add to URLs

```python
# src/bookme/services/urls.py

from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ServicePackageViewSet

router = DefaultRouter()
router.register('services', ServiceViewSet, basename='service')
router.register('packages', ServicePackageViewSet, basename='package')

urlpatterns = router.urls
```

#### 5. Register in Admin

```python
# src/bookme/services/admin.py

from django.contrib import admin
from .models import Service, ServicePackage

@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_price', 'discount_percentage', 'is_active', 'created_at']
    list_filter = ['is_active', 'valid_from', 'valid_until']
    search_fields = ['name', 'description']
    filter_horizontal = ['services']  # Nice UI for many-to-many
    readonly_fields = ['id', 'created_at', 'updated_at', 'discount_percentage']

    fieldsets = [
        ('Package Information', {
            'fields': ['name', 'description', 'services']
        }),
        ('Pricing', {
            'fields': ['original_price', 'package_price', 'discount_percentage']
        }),
        ('Availability', {
            'fields': ['is_active', 'valid_from', 'valid_until']
        }),
        ('Metadata', {
            'fields': ['id', 'metadata', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def discount_percentage(self, obj):
        return f"{obj.discount_percentage:.1f}%"
    discount_percentage.short_description = 'Discount'
```

#### 6. Create Migration and Apply

```powershell
python manage.py makemigrations services
python manage.py migrate_schemas
```

✅ **Done!** New model is ready to use.

---

## 🔍 Debugging Common Issues

### Issue: "Can't access tenant at demo.localhost"

**Solution**: Add to hosts file

Windows: `C:\Windows\System32\drivers\etc\hosts`
```
127.0.0.1  demo.localhost
127.0.0.1  test.localhost
```

Mac/Linux: `/etc/hosts`
```
127.0.0.1  demo.localhost
127.0.0.1  test.localhost
```

### Issue: "No module named 'bookme.xxx'"

**Solution**: Install package in development mode

```powershell
pip install -e ".[dev]"
```

### Issue: "Migrations not applying"

**Solution**: Use correct command

```powershell
# ❌ Wrong
python manage.py migrate

# ✅ Correct
python manage.py migrate_schemas
```

### Issue: "Can't query data in tenant"

**Solution**: Check middleware is working

```python
# In Django shell
from django.test import RequestFactory
from django_tenants.middleware import TenantMainMiddleware

# Check current schema
from django.db import connection
print(f"Current schema: {connection.schema_name}")

# Should be 'tenant_xxx', not 'public'
```

### Issue: "ForeignKey error between shared and tenant models"

**Solution**: Use UUID references instead

```python
# ❌ Don't do this
class Booking(TenantAwareModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

# ✅ Do this
class Booking(TenantAwareModel):
    user_id = models.UUIDField()
    user_email = models.EmailField()  # Denormalize
```

---

## 🧪 Writing Tests

### Test a Model

```python
# tests/test_services.py

from django_tenants.test.cases import TenantTestCase
from bookme.tenant.models import Tenant, Domain
from bookme.services.models import Service

class ServiceModelTest(TenantTestCase):

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
        """Test creating a service."""
        service = Service.objects.create(
            name='Haircut',
            price=50.00,
            duration_minutes=30
        )

        self.assertEqual(service.name, 'Haircut')
        self.assertEqual(service.price, 50.00)
        self.assertTrue(service.id)  # Has UUID

    def test_service_str(self):
        """Test string representation."""
        service = Service.objects.create(name='Test Service', price=25.00)
        self.assertEqual(str(service), 'Test Service')
```

### Test an API Endpoint

```python
# tests/test_api_services.py

from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
from bookme.services.models import Service

class ServiceAPITest(TenantTestCase):

    def setUp(self):
        super().setUp()
        self.client = TenantClient(self.tenant)

        # Create test service
        self.service = Service.objects.create(
            name='Test Service',
            price=100.00,
            duration_minutes=60
        )

    def test_list_services(self):
        """Test listing services via API."""
        response = self.client.get('/api/services/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Service')

    def test_create_service(self):
        """Test creating service via API."""
        data = {
            'name': 'New Service',
            'price': '75.00',
            'duration_minutes': 45
        }

        response = self.client.post('/api/services/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 2)
```

### Run Tests

```powershell
# All tests
pytest

# Specific file
pytest tests/test_services.py

# Specific test
pytest tests/test_services.py::ServiceModelTest::test_create_service

# With coverage
pytest --cov=src --cov-report=html

# Verbose
pytest -v -s
```

---

## 📊 Querying Data

### Query Current Tenant Data

```python
# In views or any tenant context
from bookme.services.models import Service

# Automatically scoped to current tenant
services = Service.objects.all()
active_services = Service.objects.filter(is_active=True)
```

### Query Specific Tenant Data

```python
from django.db import connection
from bookme.tenant.models import Tenant
from bookme.bookings.models import Booking

# Get tenant
tenant = Tenant.objects.get(schema_name='tenant_demo')

# Switch to tenant
connection.set_tenant(tenant)

# Query data
bookings = Booking.objects.filter(status='confirmed')

# Switch back
connection.set_schema_to_public()
```

### Aggregate Across All Tenants

```python
from django.db import connection
from bookme.tenant.models import Tenant
from bookme.bookings.models import Booking

results = []

for tenant in Tenant.objects.all():
    connection.set_tenant(tenant)

    total_bookings = Booking.objects.count()
    confirmed = Booking.objects.filter(status='confirmed').count()

    results.append({
        'tenant': tenant.name,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed,
    })

connection.set_schema_to_public()

# Use results...
for result in results:
    print(f"{result['tenant']}: {result['confirmed_bookings']} confirmed bookings")
```

---

## 🔐 Adding Authentication

### Protect API Endpoint

```python
# src/bookme/services/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Require login
```

### Custom Permission

```python
# src/bookme/core/permissions.py

from rest_framework import permissions

class IsTenantStaff(permissions.BasePermission):
    """Allow access only to tenant staff members."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check if user has membership in current tenant
        from bookme.users.models import TenantMembership
        from django.db import connection

        tenant = connection.tenant

        return TenantMembership.objects.filter(
            user=request.user,
            tenant_id=tenant.id,
            is_active=True,
            role__in=['owner', 'admin', 'manager', 'staff']
        ).exists()
```

```python
# Use in viewset
from bookme.core.permissions import IsTenantStaff

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantStaff]
    # ...
```

---

## 📦 Adding New Dependency

### Install Package

```powershell
pip install package-name
```

### Add to pyproject.toml

```toml
# pyproject.toml

dependencies = [
    "Django>=5.0,<5.1",
    "djangorestframework>=3.14.0",
    # ... existing packages ...
    "package-name>=1.0.0",  # ADD THIS
]
```

### Commit

```powershell
pip freeze > requirements.txt  # Optional, for Docker
git add pyproject.toml requirements.txt
git commit -m "Add package-name dependency"
```

---

## 🚀 Deploying Changes

### Pre-Deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Code formatted (`black .`)
- [ ] No lint errors (`ruff check .`)
- [ ] Migrations created
- [ ] Migrations tested locally
- [ ] Environment variables updated (if needed)
- [ ] Documentation updated

### Deploy Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -e ".[prod]"

# 3. Run migrations
python manage.py migrate_schemas

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Restart services
systemctl restart bookme-web
systemctl restart bookme-celery
```

---

## 💡 Tips & Tricks

### Use Django Shell Plus

```powershell
pip install django-extensions
python manage.py shell_plus
```

Automatically imports all models!

### Use iPython for Better Shell

```powershell
pip install ipython
python manage.py shell  # Now uses iPython
```

### Create Sample Data

```python
# In manage.py shell
from bookme.services.models import Service

# Create multiple services quickly
services_data = [
    {'name': 'Haircut', 'price': 30.00, 'duration_minutes': 30},
    {'name': 'Hair Coloring', 'price': 80.00, 'duration_minutes': 90},
    {'name': 'Manicure', 'price': 25.00, 'duration_minutes': 45},
]

for data in services_data:
    Service.objects.create(**data)
```

### Use Factory Boy for Tests

```python
# tests/factories.py

import factory
from bookme.services.models import Service

class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    duration_minutes = factory.Faker('random_int', min=15, max=120)

# In tests
service = ServiceFactory()
services = ServiceFactory.create_batch(10)
```

---

## 📚 Next Steps

- Read [Tenant Architecture Guide](TENANT_GUIDE.md) for deep dive
- Check [Migration Guide](MIGRATION_GUIDE.md) for database updates
- Use [Cheat Sheet](CHEAT_SHEET.md) for quick reference

**Happy coding!** 🚀
