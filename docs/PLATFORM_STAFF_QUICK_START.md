# Platform Staff - Quick Start Guide

## ✅ What Was Implemented

You now have **3 access levels** instead of just 2:

### Before (Old System)
```
❌ Superuser only → Too powerful for support staff
❌ is_staff → Could see admin login but got 403
```

### After (New System)
```
✅ Level 1: Superuser (Full control)
✅ Level 2: Platform Staff (Support team)
✅ Level 3: Tenant User (Customers)
```

## 🎯 How to Use

### Option 1: Via Django Admin (Superuser Only) ⚠️

**IMPORTANT**: Only **superusers** can manage platform staff privileges. Platform staff themselves cannot create users or grant privileges (security measure).

1. **Login as SUPERUSER** to platform admin: http://localhost:8000/admin/
2. **Go to Users** section
3. **Click "Add user"** to create new user
4. **In "Platform Access" section**, you'll see:

```
┌─────────────────────────────────────────────────────────┐
│ Platform Access                                          │
├─────────────────────────────────────────────────────────┤
│ ☑ Active                                                │
│   User can login                                         │
│                                                           │
│ ☑ Staff status                                          │
│   Required for ANY admin access                          │
│                                                           │
│ ☑ Platform staff status        ← NEW TOGGLE!            │
│   Can access platform admin (this site)                  │
│                                                           │
│ ☐ Superuser status                                      │
│   Full platform control (use sparingly!)                 │
└─────────────────────────────────────────────────────────┘
```

**For Support Staff:**
- ✅ Check: Active
- ✅ Check: Staff status
- ✅ Check: **Platform staff status** ← NEW!
- ❌ Leave unchecked: Superuser status

**For Superusers:**
- ✅ Check all boxes (auto-sets platform staff)

### Option 2: Via Management Command

```bash
# Create platform staff
python manage.py create_platform_staff support@bookme.ma

# Create superuser
python manage.py create_platform_staff admin@bookme.ma --superuser
```

### Option 3: Via Django Shell

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Update existing user
user = User.objects.get(email='support@bookme.ma')
user.is_staff = True
user.is_platform_staff = True  # ← NEW FIELD!
user.save()

# Create new platform staff
User.objects.create_user(
    email='newstaff@bookme.ma',
    password='secure-password',
    is_staff=True,
    is_platform_staff=True
)
```

## 🔒 What Each Access Level Can Do

### Superuser (`is_superuser=True`)
- ✅ Access platform admin: `localhost:8000/admin/`
- ✅ Create/edit/delete tenants
- ✅ View all users
- ✅ Modify critical settings
- ✅ Access tenant admins (if has membership)
- ⚠️ **Use sparingly** - Only 1-2 people should have this

### Platform Staff (`is_platform_staff=True`)
- ✅ Access platform admin: `localhost:8000/admin/`
- ✅ View tenants (read-only by default)
- ✅ View users (read-only)
- ❌ **CANNOT create users** (security: prevents privilege escalation)
- ❌ **CANNOT edit users** (security: prevents privilege escalation)
- ❌ **CANNOT grant privileges** (security: only superusers can)
- ❌ Cannot delete tenants
- ❌ Cannot access tenant admins (unless has TenantMembership)
- 👍 **Perfect for support team - view-only access**

### Tenant User (`is_staff=True`, no platform staff)
- ❌ Cannot access platform admin
- ✅ Access their tenant admin: `acme.localhost:8000/admin/`
- ✅ Permissions via RBAC TenantRole
- 👍 **All your customers**

## 📊 Real Example

**Scenario**: You want omar.badissy@gmail.com to help manage tenant registrations.

**Before:**
```bash
# User exists with is_staff=True
# Tries to access localhost:8000/admin/
# Gets: "403 Forbidden - not authorized"
```

**After:**
```bash
# Update the user
python manage.py shell -c "
from django.contrib.auth import get_user_model;
user = get_user_model().objects.get(email='omar.badissy@gmail.com');
user.is_platform_staff = True;
user.save()
"

# Now omar can access localhost:8000/admin/
# ✓ Can view/create tenants
# ✓ Can help with support
# ✗ Cannot delete critical data (not superuser)
```

## 🎨 Visual Guide

### Platform Admin View
When you access `localhost:8000/admin/`, you'll see:

```
╔════════════════════════════════════════════════════════╗
║        BookMe Platform Admin                          ║
╠════════════════════════════════════════════════════════╣
║  Platform Administration                              ║
║                                                        ║
║  📋 Tenant Management                                 ║
║    • Tenants                                          ║
║    • Domains                                          ║
║    • Tenant configs                                   ║
║                                                        ║
║  👥 Users                                             ║
║    • Users  ← See is_platform_staff toggle here!     ║
║    • Tenant memberships                               ║
║                                                        ║
║  🔐 RBAC                                              ║
║    • Tenant roles                                     ║
╚════════════════════════════════════════════════════════╝
```

### User List in Admin
```
┌──────────────────────────────────────────────────────────────────────┐
│ Select user to change                                                │
├──────────────────────────────────────────────────────────────────────┤
│ Email                    │ Active │ Staff │ Platform │ Super │       │
│                         │        │       │ Staff    │       │       │
├──────────────────────────────────────────────────────────────────────┤
│ abdobella977@gmail.com  │   ✓    │   ✓   │    ✓     │   ✓   │ Edit  │
│ omar.badissy@gmail.com  │   ✓    │   ✓   │    ✓     │   ✗   │ Edit  │
│ abdo@gmail.com          │   ✓    │   ✓   │    ✗     │   ✗   │ Edit  │
└──────────────────────────────────────────────────────────────────────┘
                                          ↑
                                    NEW COLUMN!
```

## 🚨 Security Checklist

### ✅ DO
- ✅ Give `is_platform_staff` to trusted support team
- ✅ Use Django Groups to limit what they can do
- ✅ Keep `is_superuser` for 1-2 senior admins only
- ✅ Regularly audit who has platform access
- ✅ Log platform staff actions for accountability

### ❌ DON'T
- ❌ Give every employee `is_superuser`
- ❌ Give tenant owners `is_platform_staff` (conflict of interest)
- ❌ Let platform staff have tenant memberships (separation of duties)

## 🎯 Common Tasks

### Add New Support Staff Member
1. Go to http://localhost:8000/admin/users/user/add/
2. Enter email and password
3. In "Access Level" section:
   - ✅ Check "Staff status"
   - ✅ Check "Platform staff status"
4. Click "Save"

### Remove Platform Access
1. Go to user in admin
2. Uncheck "Platform staff status"
3. Save
4. User can no longer access platform admin

### Promote to Superuser
1. Go to user in admin
2. Check "Superuser status"
3. Platform staff is auto-checked
4. Save
5. ⚠️ User now has FULL control

## 📞 Support

**If you see "403 Forbidden" on localhost:8000/admin/:**
1. Check: Is `is_staff=True`? (Required for ANY admin)
2. Check: Is `is_platform_staff=True`? (New requirement!)
3. Check: Is account active?

**To verify:**
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model;
u = get_user_model().objects.get(email='your@email.com');
print(f'is_staff: {u.is_staff}');
print(f'is_platform_staff: {u.is_platform_staff}');
print(f'is_superuser: {u.is_superuser}')
"
```

## 🔒 Security Measures

### Platform Staff CANNOT (by design):
- ❌ Create new users in platform admin
- ❌ Edit ANY user accounts (including own account)
- ❌ Grant `is_platform_staff` or `is_superuser` privileges
- ❌ Delete users
- ❌ Assign Django groups or permissions
- ❌ Modify their own privileges (prevents self-escalation)

### Why These Restrictions?
**Privilege escalation prevention**: Platform staff could otherwise:
1. Create a user with `is_superuser=True`
2. Edit their own account to grant `is_superuser`
3. Collude with another platform staff member
4. Grant privileges to external parties

### What Platform Staff CAN Do:
- ✅ **View** all users (read-only)
- ✅ **View** all tenants (read-only)
- ✅ Access platform admin interface
- ✅ Help with support inquiries (view-only)

### Only Superusers Can:
- ✅ Create users in platform admin
- ✅ Grant `is_platform_staff` or `is_superuser`
- ✅ Edit user privileges
- ✅ Delete users
- ✅ Assign Django groups

**See**: `docs/PLATFORM_STAFF_SECURITY.md` for full security details.

## 🎉 Success!

You now have a **professional, scalable, SECURE access control system**!

- 🏢 **Superusers**: CEO, CTO (full control)
- 🛠️ **Platform Staff**: Support, Operations (view-only)
- 👥 **Tenant Users**: All your customers (isolated)

This is the same approach used by Stripe, Shopify, AWS, and other major SaaS platforms.

**Key Security**: Platform staff have **read-only access** to prevent privilege escalation attacks.
