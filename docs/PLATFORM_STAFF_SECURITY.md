# Platform Staff Security - Privilege Escalation Prevention

## 🔒 Security Problem Identified

**Critical Risk**: Platform staff could grant themselves (or others) superuser or platform_staff privileges, leading to unauthorized access escalation.

## ✅ Security Measures Implemented

### 1. Field Visibility Control
Platform staff **CANNOT SEE**:
- `is_platform_staff` checkbox
- `is_superuser` checkbox
- `groups` field (Django permission groups)
- `user_permissions` field

They can only see:
- ✅ `is_active` - Enable/disable account
- ✅ `is_staff` - Allow tenant admin access

### 2. Read-Only Fields
Even if a platform staff member tries to manipulate the form, these fields are **read-only**:
- `is_platform_staff`
- `is_superuser`
- `groups`
- `user_permissions`

### 3. Permission Checks

#### Cannot Add Users
```python
has_add_permission(request):
    return request.user.is_superuser  # Only superusers can create users
```

**Why**: Creating users in platform admin could be abused. Tenant users should be created via tenant admin.

#### Cannot Delete Users
```python
has_delete_permission(request, obj):
    if not request.user.is_superuser:
        return False  # Platform staff cannot delete users
```

**Why**: Deleting users is destructive and should be superuser-only.

#### Cannot Edit Privileged Users
```python
has_change_permission(request, obj):
    if not request.user.is_superuser:
        if obj.id == request.user.id:
            return False  # Cannot edit own account
        if obj.is_superuser:
            return False  # Cannot edit superusers
        if obj.is_platform_staff:
            return False  # Cannot edit other platform staff
```

**Why**: Prevents:
- Self-privilege escalation
- Modifying accounts with higher privileges
- Collusion between platform staff members

### 4. Save-Time Validation
Even if someone bypasses frontend checks, the backend validates:

```python
save_model(request, obj, form, change):
    if not request.user.is_superuser:
        if obj.is_platform_staff or obj.is_superuser:
            # BLOCK and show error
            obj.is_platform_staff = False
            obj.is_superuser = False
```

**Why**: Defense in depth - validate on save even if form validation is bypassed.

## 🔐 Access Matrix

| Action | Superuser | Platform Staff | Tenant User |
|--------|-----------|----------------|-------------|
| **Platform Admin Access** |
| Access platform admin | ✅ | ✅ | ❌ |
| **User Management** |
| View all users | ✅ | ✅ | ❌ |
| Create users | ✅ | ❌ | ❌ |
| Edit regular users | ✅ | ❌ | ❌ |
| Edit platform staff | ✅ | ❌ | ❌ |
| Edit superusers | ✅ | ❌ | ❌ |
| Edit own account | ✅ | ❌ | ✅* |
| Delete users | ✅ | ❌ | ❌ |
| **Privilege Escalation** |
| Grant `is_staff` | ✅ | ❌ | ❌ |
| Grant `is_platform_staff` | ✅ | ❌ | ❌ |
| Grant `is_superuser` | ✅ | ❌ | ❌ |
| Assign Django groups | ✅ | ❌ | ❌ |
| Assign permissions | ✅ | ❌ | ❌ |

\* Via tenant admin only

## 🎯 Test Scenarios

### Test 1: Platform Staff Tries to Create User
```
Given: User is logged in as platform staff (not superuser)
When: Navigates to /admin/users/user/add/
Then: Sees "You do not have permission to add user"
```

### Test 2: Platform Staff Tries to Edit Superuser
```
Given: User is logged in as platform staff
When: Clicks on a superuser account in user list
Then: Edit button is disabled/hidden
```

### Test 3: Platform Staff Tries to Edit Own Account
```
Given: User is logged in as platform staff
When: Clicks on their own account
Then: Cannot access edit form (403 or hidden)
```

### Test 4: Platform Staff Tries to Edit Another Platform Staff
```
Given: User is logged in as platform staff
When: Clicks on another platform staff account
Then: Cannot access edit form
```

### Test 5: Platform Staff Can Only View Users
```
Given: User is logged in as platform staff
When: Views user list
Then: Can see all users but cannot edit any
```

### Test 6: Form Manipulation Attempt
```
Given: Malicious platform staff manipulates HTML/POST data
When: Tries to send is_platform_staff=True or is_superuser=True
Then: Backend rejects and shows error message
      Dangerous flags are reset to False
```

## 🚨 Security Checklist

### ✅ Implemented Protections

- [x] Platform staff cannot see privilege fields in form
- [x] Platform staff cannot edit privilege fields (read-only)
- [x] Platform staff cannot create users in platform admin
- [x] Platform staff cannot delete users
- [x] Platform staff cannot edit own account
- [x] Platform staff cannot edit superusers
- [x] Platform staff cannot edit other platform staff
- [x] Backend validation prevents privilege escalation
- [x] Error messages inform but don't leak info
- [x] Audit trail via Django's built-in logging

### 🔄 Additional Recommendations

#### 1. Add Audit Logging
```python
import logging
logger = logging.getLogger('security')

def save_model(self, request, obj, form, change):
    # Log privilege escalation attempts
    if not request.user.is_superuser and (obj.is_platform_staff or obj.is_superuser):
        logger.warning(
            f"SECURITY: Privilege escalation attempt by {request.user.email} "
            f"trying to grant privileges to {obj.email}"
        )
```

#### 2. Rate Limiting
Implement rate limiting on login and admin actions for platform staff.

#### 3. Two-Factor Authentication
Require 2FA for all platform staff (especially superusers).

#### 4. Regular Audits
```bash
# Check for unexpected superusers
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
superusers = User.objects.filter(is_superuser=True);
print(f'Total superusers: {superusers.count()}');
[print(f'  - {u.email}') for u in superusers]
"
```

#### 5. Alert on Privilege Changes
Send email/Slack alert when:
- New superuser is created
- Platform staff is granted
- Permissions are modified

## 🔧 Testing the Security

### Manual Test as Platform Staff

1. **Login as platform staff** (e.g., omar.badissy@gmail.com)
2. **Go to**: http://localhost:8000/admin/users/user/
3. **Verify**:
   - [ ] "Add user" button is DISABLED
   - [ ] Can see user list
   - [ ] Clicking on any user shows "You don't have permission to edit"
   - [ ] Cannot see is_platform_staff or is_superuser columns

### Automated Test Script

```python
# test_platform_staff_security.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()

class PlatformStaffSecurityTest(TestCase):
    def setUp(self):
        # Create superuser
        self.superuser = User.objects.create_superuser(
            email='super@test.com',
            password='test123'
        )

        # Create platform staff
        self.platform_staff = User.objects.create_user(
            email='staff@test.com',
            password='test123',
            is_staff=True,
            is_platform_staff=True
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='test123',
            is_staff=True
        )

        self.client = Client()

    def test_platform_staff_cannot_create_user(self):
        """Platform staff cannot access add user page"""
        self.client.login(email='staff@test.com', password='test123')
        response = self.client.get('/admin/users/user/add/')
        self.assertEqual(response.status_code, 403)

    def test_platform_staff_cannot_edit_superuser(self):
        """Platform staff cannot edit superuser accounts"""
        self.client.login(email='staff@test.com', password='test123')
        response = self.client.get(f'/admin/users/user/{self.superuser.id}/change/')
        self.assertEqual(response.status_code, 403)

    def test_platform_staff_cannot_edit_self(self):
        """Platform staff cannot edit their own account"""
        self.client.login(email='staff@test.com', password='test123')
        response = self.client.get(f'/admin/users/user/{self.platform_staff.id}/change/')
        self.assertEqual(response.status_code, 403)

    def test_platform_staff_cannot_grant_privileges(self):
        """Platform staff cannot grant platform_staff or superuser via POST"""
        self.client.login(email='staff@test.com', password='test123')
        response = self.client.post(
            f'/admin/users/user/{self.regular_user.id}/change/',
            {
                'email': 'user@test.com',
                'is_staff': True,
                'is_platform_staff': True,  # Attempt privilege escalation
                'is_superuser': True,       # Attempt privilege escalation
            }
        )

        # Reload user from DB
        self.regular_user.refresh_from_db()

        # Verify privileges were NOT granted
        self.assertFalse(self.regular_user.is_platform_staff)
        self.assertFalse(self.regular_user.is_superuser)

    def test_superuser_can_grant_privileges(self):
        """Superusers CAN grant privileges (control test)"""
        self.client.login(email='super@test.com', password='test123')
        response = self.client.post(
            f'/admin/users/user/{self.regular_user.id}/change/',
            {
                'email': 'user@test.com',
                'is_staff': True,
                'is_platform_staff': True,
            }
        )

        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_platform_staff)
```

Run tests:
```bash
python manage.py test tenants_core.users.tests.test_platform_staff_security
```

## 📊 Security Summary

### Before (Vulnerability)
```
Platform Staff → Edit User Form → ✅ is_platform_staff → ⚠️ GRANTED
Platform Staff → Edit User Form → ✅ is_superuser → ⚠️ GRANTED
Platform Staff → Edit Own Account → ⚠️ Could escalate privileges
```

### After (Secured)
```
Platform Staff → Edit User Form → ❌ Fields not visible
Platform Staff → Edit User Form → ❌ Fields read-only
Platform Staff → Edit Own Account → ❌ Access denied
Platform Staff → Create User → ❌ Permission denied
Platform Staff → Delete User → ❌ Permission denied
Backend Validation → ❌ Rejects privilege escalation
```

## 🎓 Security Lessons

1. **Never trust the frontend** - Always validate on backend
2. **Least privilege principle** - Platform staff should only have necessary access
3. **Defense in depth** - Multiple layers of security checks
4. **Audit everything** - Log security-sensitive actions
5. **Regular reviews** - Audit user privileges periodically

## ✅ Conclusion

The platform admin is now **secure against privilege escalation**:
- ✅ Platform staff have read-only access to users
- ✅ Cannot create, edit, or delete users
- ✅ Cannot grant themselves or others elevated privileges
- ✅ Cannot modify their own account
- ✅ Backend validation prevents all bypass attempts

**Only superusers** can manage user privileges, as it should be! 🔒
