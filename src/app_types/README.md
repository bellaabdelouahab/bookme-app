# App Types - Business-Specific Applications

## Overview
This folder contains business-type specific Django apps. Each business type (clinic, gym, etc.) has its own complete implementation with models, views, admin, and APIs tailored to that industry.

## Structure

```
app_types/
├── __init__.py
├── common/                  # Shared abstract base models
│   ├── __init__.py
│   └── models.py           # BaseBooking, BaseService, BaseStaffMember, BaseCategory
│
├── clinic/                 # Medical clinic application
│   ├── __init__.py
│   ├── apps.py            # ClinicConfig
│   ├── models.py          # TODO: ClinicAppointment, Doctor, MedicalRecord, Patient
│   ├── admin.py           # TODO: Admin interface
│   ├── views.py           # TODO: API views
│   ├── serializers.py     # TODO: REST serializers
│   ├── urls.py            # TODO: URL routing
│   └── migrations/
│
└── gym/                    # Gym/fitness center application
    ├── __init__.py
    ├── apps.py            # GymConfig
    ├── models.py          # TODO: GymMembership, Trainer, WorkoutPlan, Member
    ├── admin.py           # TODO: Admin interface
    ├── views.py           # TODO: API views
    ├── serializers.py     # TODO: REST serializers
    ├── urls.py            # TODO: URL routing
    └── migrations/
```

## Common Models (app_types/common/models.py)

Abstract base models that all business-type apps inherit from:

### BaseBooking
- **Purpose**: Universal booking/appointment fields
- **Fields**: customer, booking_date, start_time, end_time, status, notes, cancellation tracking
- **Methods**: `get_duration_minutes()`, `can_cancel()`, validation
- **Used by**: ClinicAppointment, GymMembership, etc.

### BaseService
- **Purpose**: Universal service/offering fields
- **Fields**: name, description, base_price, duration_minutes, is_active, display_order
- **Used by**: Medical services, gym classes, etc.

### BaseStaffMember
- **Purpose**: Universal staff/provider fields
- **Fields**: user, display_name, title, bio, phone, email, profile_photo, is_active, accepts_bookings
- **Used by**: Doctor, Trainer, etc.

### BaseCategory
- **Purpose**: Universal categorization
- **Fields**: name, description, parent (hierarchical), display_order, is_active
- **Used by**: Service categories, workout categories, etc.

## How to Use

### 1. Extending Base Models (Example for Clinic)

```python
# app_types/clinic/models.py

from app_types.common.models import BaseBooking, BaseStaffMember

class Doctor(BaseStaffMember):
    """Extends BaseStaffMember with clinic-specific fields."""
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    board_certifications = models.JSONField(default=list)

    class Meta:
        db_table = 'clinic_doctor'
        verbose_name = 'Doctor'

class ClinicAppointment(BaseBooking):
    """Extends BaseBooking with clinic-specific fields."""
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    chief_complaint = models.TextField()
    diagnosis = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    vital_signs = models.JSONField(default=dict)

    class Meta:
        db_table = 'clinic_appointment'
        verbose_name = 'Appointment'
```

### 2. Extending Base Models (Example for Gym)

```python
# app_types/gym/models.py

from app_types.common.models import BaseBooking, BaseStaffMember

class Trainer(BaseStaffMember):
    """Extends BaseStaffMember with gym-specific fields."""
    certifications = models.JSONField(default=list)
    specializations = models.JSONField(default=list)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'gym_trainer'
        verbose_name = 'Trainer'

class GymMembership(BaseBooking):
    """Extends BaseBooking for gym memberships."""
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True)
    membership_type = models.CharField(max_length=50)
    access_hours = models.CharField(max_length=50)
    locker_number = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'gym_membership'
        verbose_name = 'Membership'
```

## Implementation Status

### ✅ Completed
- [x] Folder structure created
- [x] Base abstract models (BaseBooking, BaseService, BaseStaffMember, BaseCategory)
- [x] App configs (ClinicConfig, GymConfig)
- [x] Placeholder files for all apps

### ⏳ TODO
- [ ] Implement clinic models (ClinicAppointment, Doctor, MedicalRecord, Patient)
- [ ] Implement gym models (GymMembership, Trainer, WorkoutPlan, Member)
- [ ] Create admin interfaces for both apps
- [ ] Create REST API views and serializers
- [ ] Create URL routing
- [ ] Generate initial migrations
- [ ] Integrate with settings.py (dynamic app loading)
- [ ] Create middleware for app-type access control
- [ ] Write tests

## Key Design Principles

1. **Inheritance**: All business models inherit from common base models
2. **Separation**: Each business type is a completely separate Django app
3. **Extensibility**: Easy to add new business types by copying structure
4. **Type Safety**: Different table names (clinic_appointment vs gym_membership)
5. **API Isolation**: Different endpoints (/api/clinic/ vs /api/gym/)

## Next Steps

1. **Implement Clinic Models**
   - Create concrete models extending base classes
   - Add clinic-specific fields and methods
   - Focus on medical domain (appointments, diagnoses, prescriptions)

2. **Implement Gym Models**
   - Create concrete models extending base classes
   - Add gym-specific fields and methods
   - Focus on fitness domain (memberships, workout plans, trainers)

3. **Settings Integration**
   - Update `settings.py` with dynamic app loading
   - Create `APP_TYPE_APPS` dictionary
   - Implement middleware for tenant-based app activation

4. **Generate Migrations**
   ```bash
   python manage.py makemigrations clinic
   python manage.py makemigrations gym
   ```

5. **Test Schema Creation**
   ```python
   # Create clinic tenant
   tenant = Tenant.objects.create(
       schema_name='clinic_example',
       app_type='clinic'
   )
   # Only clinic tables created in tenant schema

   # Create gym tenant
   tenant = Tenant.objects.create(
       schema_name='gym_example',
       app_type='gym'
   )
   # Only gym tables created in tenant schema
   ```

## Benefits of This Architecture

✅ **Clean Separation**: Clinic code never mixes with gym code
✅ **Different Models**: `ClinicAppointment` vs `GymMembership` - completely different
✅ **Different APIs**: `/api/clinic/appointments/` vs `/api/gym/memberships/`
✅ **Optimal Schemas**: Clinic tenant has no `gym_membership` table
✅ **Code Reuse**: Base models prevent duplication of common fields
✅ **Type Safety**: Cannot accidentally mix clinic and gym data
✅ **Independent Evolution**: Change clinic without affecting gym

## Adding a New Business Type

To add a new business type (e.g., "restaurant"):

1. Create folder: `app_types/restaurant/`
2. Copy structure from `clinic/` or `gym/`
3. Create `RestaurantConfig` in `apps.py`
4. Extend base models with restaurant-specific fields
5. Implement views, serializers, admin
6. Add to `APP_TYPE_APPS` in settings
7. Generate migrations
8. Done!
