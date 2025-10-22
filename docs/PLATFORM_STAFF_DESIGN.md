# Platform Staff Access Design

## Problem Statement

We need to allow support staff to access the public admin (`localhost:8000/admin/`) to help manage tenant registrations and platform operations, WITHOUT giving them full `is_superuser` access.

## Solution: Three-Tier Access Model

```
┌─────────────────────────────────────────────────────────────┐
│                   Platform Access Levels                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Level 1: SUPERUSER (Full Platform Admin)                   │
│  ├─ is_superuser = True                                      │
│  ├─ is_platform_staff = True (auto-set)                      │
│  ├─ Can: EVERYTHING                                          │
│  └─ Who: CEO, CTO (1-2 people)                               │
│                                                               │
│  Level 2: PLATFORM STAFF (Support/Operations)                │
│  ├─ is_superuser = False                                     │
│  ├─ is_platform_staff = True                                 │
│  ├─ Can: View/create tenants, support operations             │
│  └─ Who: Support staff, operations team (5-10 people)        │
│                                                               │
│  Level 3: TENANT USER (Customer)                             │
│  ├─ is_superuser = False                                     │
│  ├─ is_platform_staff = False                                │
│  ├─ is_staff = True (for tenant admin access)                │
│  └─ Can: Access own tenant admin via RBAC                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Step 1: Add `is_platform_staff` Field to User Model

```python
# tenants_core/users/models.py
class User(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...

    is_platform_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can access the platform admin. "
                  "Platform staff can manage tenants but don't have full superuser access."
    )
```

### Step 2: Update PublicAdminSite Permission Check

```python
# tenants_core/core/admin_site.py
class PublicAdminSite(AdminSite):
    site_header = "BookMe Platform Admin"
    site_title = "BookMe Platform Admin"
    index_title = "Platform Administration"

    def has_permission(self, request):
        """
        Allow access to:
        1. Superusers (full access)
        2. Platform staff (limited by Django permissions)
        """
        return bool(
            request.user
            and request.user.is_active
            and (request.user.is_superuser or request.user.is_platform_staff)
        )
```

### Step 3: Create Platform Staff Groups with Permissions

```python
# Management command: create_platform_staff_groups.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Group 1: Tenant Manager (can manage tenants)
tenant_manager = Group.objects.create(name='Platform: Tenant Manager')
tenant_ct = ContentType.objects.get(app_label='tenant', model='tenant')
tenant_manager.permissions.add(
    Permission.objects.get(content_type=tenant_ct, codename='view_tenant'),
    Permission.objects.get(content_type=tenant_ct, codename='add_tenant'),
    Permission.objects.get(content_type=tenant_ct, codename='change_tenant'),
)

# Group 2: Support Staff (read-only)
support_staff = Group.objects.create(name='Platform: Support Staff')
support_staff.permissions.add(
    Permission.objects.get(content_type=tenant_ct, codename='view_tenant'),
    # View users, memberships for support
)

# Group 3: Platform Admin (everything except dangerous operations)
platform_admin = Group.objects.create(name='Platform: Admin')
# Add all permissions except delete_tenant
```

### Step 4: Update Middleware to Allow Platform Staff on Public

```python
# tenants_core/core/middleware.py - TenantAdminAccessMiddleware
def process_request(self, request):
    # ... existing code ...

    # On public schema, allow superusers AND platform staff
    schema_name = getattr(tenant, "schema_name", None)
    if schema_name in (None, "public"):
        # Check if user has platform access
        if user.is_superuser or getattr(user, 'is_platform_staff', False):
            return None
        # Otherwise block access
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden(
            "You do not have platform admin access. "
            "Contact a superuser to grant you platform staff permissions."
        )

    # ... rest of tenant admin logic ...
```

### Step 5: Register Models with Granular Permissions

```python
# tenants_core/tenant/admin.py
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    # ... existing code ...

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete tenants (dangerous!)"""
        return request.user.is_superuser

    def has_add_permission(self, request):
        """Platform staff can create tenants"""
        return request.user.is_superuser or request.user.has_perm('tenant.add_tenant')

    def has_change_permission(self, request, obj=None):
        """Platform staff can edit tenants"""
        return request.user.is_superuser or request.user.has_perm('tenant.change_tenant')
```

## Usage Examples

### Create a Platform Staff User

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Create support staff
support_user = User.objects.create_user(
    email='support@bookme.ma',
    password='secure-password',
    is_staff=True,  # Required for admin access
    is_platform_staff=True,  # NEW FIELD
    is_superuser=False  # NOT a superuser
)

# Assign to group
support_group = Group.objects.get(name='Platform: Support Staff')
support_user.groups.add(support_group)
```

### Create Tenant Manager

```python
tenant_manager = User.objects.create_user(
    email='manager@bookme.ma',
    password='secure-password',
    is_staff=True,
    is_platform_staff=True,
    is_superuser=False
)

manager_group = Group.objects.get(name='Platform: Tenant Manager')
tenant_manager.groups.add(manager_group)
```

## Permission Matrix

| Action | Superuser | Platform Staff (Tenant Manager) | Platform Staff (Support) | Tenant User |
|--------|-----------|--------------------------------|--------------------------|-------------|
| Access public admin | ✅ | ✅ | ✅ | ❌ |
| View all tenants | ✅ | ✅ | ✅ | ❌ |
| Create tenant | ✅ | ✅ | ❌ | ❌ |
| Edit tenant | ✅ | ✅ | ❌ | ❌ |
| Delete tenant | ✅ | ❌ | ❌ | ❌ |
| View all users | ✅ | ✅ | ✅ | ❌ |
| Access tenant admin | ✅* | ❌** | ❌** | ✅ |

\* If they have a TenantMembership
\*\* Unless they also have a TenantMembership (they can be both)

## Security Considerations

### ✅ Best Practices

1. **Minimal Platform Staff**
   - Only trusted employees get `is_platform_staff=True`
   - Regularly audit this list

2. **Use Groups for Permissions**
   - Don't assign permissions directly to users
   - Use groups for easier management

3. **Superuser Reserved for Critical Operations**
   - Only 1-2 people should have `is_superuser=True`
   - Log all superuser actions

4. **Separate Platform and Tenant Access**
   - Platform staff should NOT have tenant memberships (conflict of interest)
   - If needed, create separate user accounts

### ❌ Anti-Patterns

1. **Don't give all platform staff superuser**
   - Huge security risk
   - Use groups instead

2. **Don't let tenant owners become platform staff**
   - They could see other tenants' data
   - Keep roles separate

3. **Don't skip permission checks**
   - Always check `has_perm()` in admin
   - Don't assume `is_platform_staff` means unlimited access

## Migration Script

```python
# Migration: 0007_add_is_platform_staff.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0006_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_platform_staff',
            field=models.BooleanField(
                default=False,
                help_text='Designates whether the user can access the platform admin.'
            ),
        ),
        # Auto-set is_platform_staff=True for existing superusers
        migrations.RunPython(
            lambda apps, schema_editor: apps.get_model('users', 'User').objects.filter(
                is_superuser=True
            ).update(is_platform_staff=True),
            migrations.RunPython.noop
        ),
    ]
```

## Alternative: Public as a Tenant (Advanced)

If you prefer treating public as a tenant (your original idea):

### Pros
- Consistent RBAC everywhere
- More granular permission control
- Can use same role system

### Implementation
1. Keep "Public" tenant in database (it already exists)
2. Create special roles for public tenant:
   - "Platform Admin" role
   - "Tenant Manager" role
   - "Support Staff" role
3. Give platform staff TenantMembership to public tenant
4. Modify middleware to check public tenant memberships

This is more complex but gives you maximum flexibility. Use this approach if:
- You need very granular permissions on public admin
- You want to reuse RBAC system everywhere
- You plan to have many platform staff with different roles

## Recommendation

**For most cases: Use `is_platform_staff` + Django Groups**

- Simple
- Standard Django approach
- Clear separation between platform and tenant admin
- Easy to explain to team

**Use "Public as Tenant" if:**
- You have 10+ platform staff with varied roles
- You need audit trails on platform actions
- You want to reuse RBAC system investment

## Summary

```python
# Recommended approach
user = User.objects.create(
    email='support@bookme.ma',
    is_staff=True,
    is_platform_staff=True,  # ← New field
    is_superuser=False
)
user.groups.add(Group.objects.get(name='Platform: Support Staff'))

# Access control
if user.is_superuser or user.is_platform_staff:
    # Can access public admin
    # Permissions controlled by Django groups
```

This gives you:
- ✅ Granular control without superuser
- ✅ Standard Django patterns
- ✅ Easy to understand and maintain
- ✅ Scalable as team grows
