# RBAC (Role-Based Access Control) System - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [System Roles](#system-roles)
3. [Permission Hierarchy](#permission-hierarchy)
4. [Admin Interface](#admin-interface)
5. [Custom Roles](#custom-roles)
6. [Security Model](#security-model)
7. [Management Commands](#management-commands)
8. [Troubleshooting](#troubleshooting)

---

## Overview

BookMe uses a hierarchical Role-Based Access Control (RBAC) system where permissions are organized into roles. Each tenant has 5 system roles plus the ability to create unlimited custom roles.

### Key Concepts
- **Roles**: Groups of permissions (e.g., Owner, Admin, Manager)
- **Permissions**: Django permissions (e.g., `add_booking`, `view_customer`)
- **Hierarchy**: Each role is a subset of the role above it
- **System Roles**: Protected roles created automatically (Owner, Admin, Manager, Staff, Viewer)
- **Custom Roles**: Tenant-specific roles created by Owner

---

## System Roles

Five system roles are automatically created for each tenant:

### 1. Owner (41 permissions)
**Purpose**: Full control of tenant account
**Capabilities**:
- User and membership management
- Role management
- Tenant settings
- All business operations

**Key Permissions**:
- User: add, change, view
- Membership: add, change, delete, view
- Role: add, change, delete, view
- All business entity permissions

### 2. Admin (28 permissions)
**Purpose**: Business operations management
**Capabilities**:
- View users/memberships/roles (no modify)
- Manage services, staff, customers
- Full booking management
- Create/edit notifications
- View payments

**Key Permissions**:
- Services: add, change, delete, view
- Staff: add, change, delete, view
- Customers: add, change, delete, view
- Bookings: add, change, delete, view
- View-only: users, memberships, roles, payments

### 3. Manager (18 permissions)
**Purpose**: Daily operations
**Capabilities**:
- Manage bookings and customers
- View and coordinate staff
- Handle notifications
- View users and memberships

**Key Permissions**:
- Bookings: add, change, delete, view
- Customers: add, change, view
- Staff: change, view
- Services: change, view
- Resources: change, view

### 4. Staff (9 permissions)
**Purpose**: Personal work management
**Capabilities**:
- View own schedule
- Manage assigned bookings
- View customers and resources
- View payments

**Key Permissions**:
- Bookings: change, view
- View-only: users, services, staff, customers, payments, resources

### 5. Viewer (7 permissions)
**Purpose**: Read-only access
**Capabilities**:
- View all business data
- No create/edit/delete operations

**Key Permissions**:
- View-only: services, staff, customers, bookings, notifications, payments, resources

---

## Permission Hierarchy

The roles follow a strict hierarchical structure where each lower role is a **proper subset** of the role above it:

```
Owner (41 perms)
  └── Admin (28 perms)
      └── Manager (18 perms)
          └── Staff (9 perms)
              └── Viewer (7 perms)
```

**Mathematical Relationship**: `Viewer ⊆ Staff ⊆ Manager ⊆ Admin ⊆ Owner`

### Permission Categories

Permissions are organized by Django models (11 categories):

1. **booking** - Booking management
2. **customer** - Customer management
3. **notification** - Communication management
4. **payment** - Payment tracking
5. **resource** - Resource management
6. **service** - Service catalog
7. **staffmember** - Staff management
8. **tenant** - Tenant settings (Owner only)
9. **tenantmembership** - Team member management (Owner only)
10. **tenantrole** - Role management (Owner only)
11. **user** - User account management (Owner only)

---

## Admin Interface

### For Tenant Admins

**URL**: `http://yoursubdomain.localhost:8000/admin/`

**Sections Available**:
- **Users** - View/create users (basic info only, no permissions)
- **Team Members** - Assign roles to users
- **Tenant Roles** - View system roles, create custom roles
- **Services** - Manage services (if has permission)
- **Staff** - Manage staff members (if has permission)
- **Customers** - Manage customers (if has permission)
- **Bookings** - Manage bookings (if has permission)
- More sections based on assigned role

**Viewing System Roles**:
- Click on Owner, Admin, Manager, Staff, or Viewer
- All fields are **read-only** (gray/disabled)
- See list of permissions assigned to each role
- Cannot modify system roles

**Creating Custom Roles**:
1. Go to Tenant Roles → Add Tenant Role
2. Enter role name (e.g., "Receptionist")
3. Enter description
4. Select permissions from filtered list (40 available)
5. Set active status
6. Click Save

**Filtered Permissions**:
Only business-relevant permissions appear in dropdown:
- ✅ Services, Staff, Customers, Bookings
- ✅ Communications, Payments, Resources
- ❌ User management (Owner only)
- ❌ Membership management (Owner only)
- ❌ Role management (Owner only)

### For Super Admins

**URL**: `http://localhost:8000/admin/` (public domain)

**Capabilities**:
- Full access to all tenants
- Manage tenant records
- Full user and membership management
- View/edit all system roles

---

## Custom Roles

### Creating Custom Roles

Custom roles allow tenants to define specific permission sets for their business needs.

**Requirements**:
- Must be Owner or have `add_tenantrole` permission
- Role name must be unique within tenant

**Steps**:
1. Navigate to Admin → Tenant Roles → Add Tenant Role
2. Fill in:
   - **Name**: Role name (e.g., "Therapist", "Receptionist")
   - **Description**: What this role can do
   - **Permissions**: Select from 40 filtered permissions
   - **Active**: Enable/disable role
3. Click Save

**Example Custom Roles**:

**Receptionist**:
- Permissions: add/view bookings, add/view customers, view services, view staff
- Use case: Front desk staff managing appointments

**Therapist**:
- Permissions: view/change bookings, view customers, view own schedule
- Use case: Service providers managing their appointments

**Accountant**:
- Permissions: view bookings, view customers, view/change payments
- Use case: Financial management

### Assigning Custom Roles

1. Navigate to Admin → Team Members
2. Select team member or add new
3. Choose role from dropdown (shows system + custom roles)
4. Save

**Note**: Users can only have ONE role per tenant.

---

## Security Model

### Design Principles

1. **Role-Based Only**: Permissions assigned through roles, not directly to users
2. **Tenant Isolation**: Roles and memberships scoped by tenant_id
3. **Hierarchical**: Lower roles are subsets of higher roles
4. **Least Privilege**: Users get minimum permissions needed
5. **Owner Protection**: Critical permissions restricted to Owner only

### Sensitive Permissions (Owner Only)

These permissions are **excluded** from custom role creation:

**User Management**:
- `add_user`, `change_user`, `delete_user`

**Membership Management**:
- `add_tenantmembership`, `change_tenantmembership`, `delete_tenantmembership`

**Role Management**:
- `add_tenantrole`, `change_tenantrole`, `delete_tenantrole`

**Rationale**: Prevents privilege escalation and ensures Owner maintains control.

### Self-Edit Prevention

Team Members admin prevents users from:
- ❌ Editing their own role (prevents privilege escalation)
- ❌ Deleting their own membership (prevents lockout)
- ✅ Viewing their own membership (read-only)

---

## Management Commands

### Fix System Roles

Updates system roles for all tenants with corrected permissions.

```bash
# Dry run (see what would change)
python manage.py fix_system_roles --dry-run

# Apply changes
python manage.py fix_system_roles
```

**Use Cases**:
- After updating `SYSTEM_ROLES_CONFIG` in signals.py
- Fixing permission hierarchy issues
- Applying security updates to existing tenants

**Output**:
```
================================================================================
Updating System Roles for All Tenants
================================================================================

Found 2 tenant(s) to process

[1/2] Processing tenant: Example Tenant
  [UPDATE] Admin:
    Current: 32 permissions
    New:     28 permissions
    Removed: 4 permissions
             - add_user
             - change_user
             - add_tenantmembership
             - change_tenantmembership
    [SAVED]

================================================================================
Summary
================================================================================
Tenants processed: 2
Roles updated:     2
```

### Ensure System Roles

Creates missing system roles for tenants (if any).

```bash
python manage.py ensure_system_roles
```

---

## Troubleshooting

### Issue: "You don't have permission to view or edit anything"

**Cause**: User has no role assigned or role has no permissions.

**Solution**:
1. Check Team Members - verify user has a role assigned
2. Check Tenant Roles - verify role has permissions
3. Verify role is active (`is_active=True`)

### Issue: Permissions not working after role assignment

**Cause**: Permission format mismatch or backend not configured.

**Solution**:
1. Verify `AUTHENTICATION_BACKENDS` includes `TenantRolePermissionBackend`
2. Check that permissions in role use format: `app_label.codename`
3. Restart Django server

### Issue: Cannot create custom role - JSON validation error

**Cause**: Form field configuration issue.

**Solution**: Fixed in code - `permissions` field explicitly excluded from ModelForm Meta.

### Issue: KeyError when viewing system roles

**Cause**: Form field initialization order.

**Solution**: Fixed in code - permissions field created in `__init__` method.

### Issue: Hierarchy validation fails

**Symptom**: Lower role has permissions that higher role doesn't have.

**Solution**:
1. Run hierarchy analysis:
   ```bash
   python manage.py shell
   >>> from tenants_core.rbac.signals import SYSTEM_ROLES_CONFIG
   >>> # Check permissions manually
   ```
2. Fix `SYSTEM_ROLES_CONFIG` in `signals.py`
3. Run `python manage.py fix_system_roles`

### Issue: Admin can manage users (security risk)

**Cause**: Admin role has sensitive permissions.

**Solution**: Already fixed - Admin role only has view permissions for users/memberships.

---

## Technical Implementation

### Files

**Models**: `src/tenants_core/rbac/models.py`
- `TenantRole` - Role definitions with JSONField permissions

**Admin**: `src/tenants_core/rbac/admin.py`
- `TenantRoleAdminForm` - Custom form with permission filtering
- `TenantRoleAdmin` - Admin interface with readonly system roles

**Backend**: `src/tenants_core/rbac/backends.py`
- `TenantRolePermissionBackend` - Permission checking logic

**Signals**: `src/tenants_core/rbac/signals.py`
- `SYSTEM_ROLES_CONFIG` - System role definitions
- Auto-creates roles on tenant creation

**Management**: `src/tenants_core/rbac/management/commands/`
- `fix_system_roles.py` - Update existing system roles

### Permission Format

Permissions stored as JSON array of codenames:
```json
["add_booking", "change_booking", "view_booking", "view_customer"]
```

Converted to Django format when checking:
```python
["bookings.add_booking", "bookings.change_booking", ...]
```

### Backend Logic

```python
def has_perm(self, user, perm, obj=None):
    if not user.is_active:
        return False

    # Get user's role for current tenant
    membership = TenantMembership.objects.filter(
        user=user,
        tenant_id=tenant.id,
        is_active=True
    ).first()

    if not membership or not membership.tenant_role:
        return False

    # Check if permission in role's permissions
    role = membership.tenant_role
    if perm in formatted_permissions(role.permissions):
        return True

    return False
```

---

## Best Practices

### For Developers

1. **Always use roles** - Never assign permissions directly to users
2. **Maintain hierarchy** - Ensure lower roles ⊆ higher roles
3. **Test permission checks** - Verify `user.has_perm()` works correctly
4. **Use permission decorators** - `@permission_required('bookings.add_booking')`
5. **Filter querysets** - Ensure tenant isolation in all queries

### For Tenant Owners

1. **Use system roles first** - They cover 90% of use cases
2. **Create custom roles sparingly** - Too many roles become hard to manage
3. **Document custom roles** - Add clear descriptions
4. **Review permissions regularly** - Audit who has access to what
5. **Use least privilege** - Give minimum permissions needed

### For System Administrators

1. **Backup before changes** - Before running `fix_system_roles`
2. **Test in staging** - Verify permission changes in non-production
3. **Monitor permission usage** - Check logs for denied permissions
4. **Keep roles updated** - Apply security patches promptly
5. **Document customizations** - Record any changes to system roles

---

## Changelog

### October 21, 2025
- ✅ Fixed hierarchy: Staff now includes `view_payment`
- ✅ Security fix: Removed user/membership permissions from Admin
- ✅ Fixed KeyError in admin interface
- ✅ Fixed JSON validation error for custom roles
- ✅ Created `fix_system_roles` management command
- ✅ Applied fixes to all existing tenants

### Previous Updates
- Implemented TenantRole model with JSONField permissions
- Created custom permission backend
- Built admin interface with permission filtering
- Added automatic system role creation on tenant signup

---

## Summary

The RBAC system provides:
- ✅ Hierarchical permission structure
- ✅ 5 system roles covering common use cases
- ✅ Unlimited custom roles for specific needs
- ✅ Secure permission management (Owner-only sensitive perms)
- ✅ Easy-to-use admin interface
- ✅ Tenant isolation and security
- ✅ Flexible and extensible architecture

For questions or issues, refer to the troubleshooting section or check the codebase documentation.
