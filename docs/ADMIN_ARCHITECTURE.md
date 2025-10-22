# Admin Architecture

## Overview

BookMe uses a **dual admin system** to separate platform administration from tenant management.

## Two Admin Sites

### 1. Public Admin (Super Admin)
- **URL**: `http://localhost:8000/admin/`
- **Purpose**: Platform-wide administration
- **Access**: Only `is_superuser=True` users
- **Scope**: Global - manages all tenants
- **Features**:
  - Create/manage tenants
  - View all users across platform
  - Manage tenant memberships
  - Platform configuration

### 2. Tenant Admin (Tenant Admin)
- **URL**: `http://<tenant>.localhost:8000/admin/`
- **Purpose**: Tenant-specific management
- **Access**: Users with RBAC permissions via `TenantRole`
- **Scope**: Tenant-isolated - only sees own data
- **Features**:
  - Manage services, bookings, customers
  - Assign roles to team members
  - Tenant-specific configuration

## Security Model

```
┌──────────────────────────────────────────────────────────────┐
│                      User Security Layers                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Layer 1: Django Authentication (users_user)                 │
│  ├─ is_superuser: Platform admin access                      │
│  ├─ is_staff: Required for ANY admin access                  │
│  └─ is_active: Account enabled                               │
│                                                               │
│  Layer 2: Tenant Membership (users_tenant_membership)        │
│  ├─ tenant_id: Which tenant(s) user belongs to               │
│  ├─ tenant_role_id: FK to rbac_tenant_role                   │
│  └─ is_active: Membership active                             │
│                                                               │
│  Layer 3: RBAC Permissions (rbac_tenant_role)                │
│  ├─ permissions: JSONField with codenames                    │
│  ├─ role_type: owner/admin/manager/staff/viewer/custom       │
│  └─ tenant_id: Isolated per tenant                           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## User Types

### Platform Administrator (Superuser)
```python
User(
    email="admin@bookme.ma",
    is_superuser=True,  # ← Key flag for public admin
    is_staff=True,
    is_active=True
)
# Has NO TenantMembership - operates at platform level
```

**Access**:
- ✅ Public admin (`localhost:8000/admin/`)
- ❌ Tenant admin (no membership)

### Tenant Owner
```python
User(
    email="owner@acme.com",
    is_superuser=False,  # ← NOT a platform admin
    is_staff=True,       # ← Required for admin access
    is_active=True
)
TenantMembership(
    user=user,
    tenant_id=acme_tenant_id,
    tenant_role=owner_role  # ← "Owner" role with all permissions
)
```

**Access**:
- ❌ Public admin (not superuser)
- ✅ Tenant admin (`acme.localhost:8000/admin/`)

### Tenant Staff
```python
User(
    email="staff@acme.com",
    is_superuser=False,
    is_staff=True,
    is_active=True
)
TenantMembership(
    user=user,
    tenant_id=acme_tenant_id,
    tenant_role=staff_role  # ← "Staff" role with limited permissions
)
```

**Access**:
- ❌ Public admin (not superuser)
- ✅ Tenant admin with limited permissions

## Permission Flow

### Public Admin Permission Check
```python
# In PublicAdminSite.has_permission()
def has_permission(self, request):
    return bool(
        request.user
        and request.user.is_active
        and request.user.is_superuser  # ← Only superusers
    )
```

### Tenant Admin Permission Check
```python
# In TenantRolePermissionBackend.has_perm()
def has_perm(self, user_obj, perm, obj=None):
    # 1. Get current tenant from connection.tenant
    # 2. Find TenantMembership for user + tenant
    # 3. Get permissions from membership.tenant_role
    # 4. Check if perm in role permissions
    return perm in self.get_all_permissions(user_obj)
```

## Best Practices

### ✅ DO

1. **Keep superuser flag exclusive**
   - Only platform administrators get `is_superuser=True`
   - Typically 1-2 people for the entire platform

2. **Use RBAC for all tenant permissions**
   - Create custom roles as needed
   - Assign via TenantMembership

3. **Set is_staff=True for tenant users**
   - Required for admin panel access
   - Does NOT grant any permissions by itself

4. **Audit superuser access regularly**
   ```sql
   SELECT email, is_superuser, last_login
   FROM users_user
   WHERE is_superuser = true;
   ```

### ❌ DON'T

1. **Never give tenant owners is_superuser**
   - Huge security risk
   - They could access other tenants' data
   - Use "Owner" role instead

2. **Don't mix Django permissions with RBAC**
   - Django permissions (`auth_permission`) - for public admin only
   - RBAC (`TenantRole`) - for tenant admin only

3. **Don't use Django Groups for tenants**
   - Groups are not tenant-isolated
   - Use `TenantRole` instead

## Creating Users

### Platform Administrator
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Only do this for trusted platform admins!
admin = User.objects.create_superuser(
    email="admin@bookme.ma",
    password="secure-password"
)
# is_superuser=True, is_staff=True automatically set
```

### Tenant Owner (During Tenant Creation)
```python
# Automatically created by TenantRegistrationView
tenant = Tenant.objects.create(name="Acme", schema_name="tenant_acme")
user = User.objects.create_user(
    email="owner@acme.com",
    password="password",
    is_staff=True  # ← Required for admin access
)
owner_role = TenantRole.objects.get(tenant_id=tenant.id, role_type='owner')
TenantMembership.objects.create(
    user=user,
    tenant_id=tenant.id,
    tenant_role=owner_role
)
```

### Tenant Staff Member
```python
# Created via tenant admin by owner/admin
user = User.objects.create_user(
    email="staff@acme.com",
    password="password",
    is_staff=True
)
staff_role = TenantRole.objects.get(
    tenant_id=request.tenant.id,
    role_type='staff'
)
TenantMembership.objects.create(
    user=user,
    tenant_id=request.tenant.id,
    tenant_role=staff_role
)
```

## Troubleshooting

### "I can't access the admin panel"

1. Check `is_staff=True`:
   ```python
   user.is_staff = True
   user.save()
   ```

2. Check tenant membership exists:
   ```python
   TenantMembership.objects.filter(user=user, tenant_id=tenant.id)
   ```

3. Check role has permissions:
   ```python
   membership.tenant_role.permissions
   # Should include the permissions you need
   ```

### "Tenant owner can access public admin"

🚨 **CRITICAL SECURITY ISSUE** - Revoke immediately:
```python
user = User.objects.get(email="owner@acme.com")
user.is_superuser = False
user.save()
```

### "Superuser can't access tenant admin"

This is normal! Superusers don't have tenant memberships by default. Options:

1. **Create a membership** (recommended):
   ```python
   TenantMembership.objects.create(
       user=superuser,
       tenant_id=tenant.id,
       tenant_role=owner_role
   )
   ```

2. **Add bypass in middleware** (not recommended):
   ```python
   # In TenantAdminAccessMiddleware
   if request.user.is_superuser:
       return  # Allow access
   ```

## Migration from Legacy System

If you have users with old `role` CharField:

```python
# Migration to populate tenant_role from legacy role field
from tenants_core.rbac.models import TenantRole
from tenants_core.users.models import TenantMembership

for membership in TenantMembership.objects.filter(tenant_role__isnull=True):
    role_map = {
        'owner': 'Owner',
        'admin': 'Admin',
        'manager': 'Manager',
        'staff': 'Staff',
        'viewer': 'Viewer'
    }
    role_name = role_map.get(membership.role, 'Staff')
    tenant_role = TenantRole.objects.get(
        tenant_id=membership.tenant_id,
        name=role_name,
        is_system=True
    )
    membership.tenant_role = tenant_role
    membership.save()
```

## Summary

| Feature | Public Admin | Tenant Admin |
|---------|--------------|--------------|
| URL | `localhost:8000/admin/` | `<tenant>.localhost:8000/admin/` |
| Access Control | `is_superuser=True` | RBAC via `TenantRole` |
| Scope | Platform-wide | Tenant-isolated |
| User Table Flag | `is_superuser` | `is_staff` |
| Permission System | Django permissions | RBAC (JSON permissions) |
| Who Uses It | Platform admins (1-2 people) | Tenant owners, staff (many) |
| Security Risk | HIGH - Full access | LOW - Isolated per tenant |

**Key Takeaway**: Never confuse the two! Platform admins (`is_superuser`) manage the infrastructure. Tenant users (RBAC) manage their business.
