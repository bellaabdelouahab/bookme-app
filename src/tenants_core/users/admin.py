"""
User and Team Member admin interfaces.

This module provides two admin sites:
1. Super Admin (public_admin_site): Full access with UserAdmin, TenantMembershipAdmin
2. Tenant Admin (admin.site): Restricted access with UserProfileAdmin, TeamMemberAdmin

Tenant admins can:
- View/create users (basic info only, no permissions)
- Assign roles to team members via TeamMemberAdmin
- Cannot edit their own membership (prevents privilege escalation)
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import connection

from tenants_core.tenant.models import Tenant

from .models import TenantMembership, User


class TenantMembershipAdminForm(forms.ModelForm):
    """Custom form for TenantMembership with tenant dropdown."""

    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all().order_by('name'),
        required=True,
        help_text="Select the tenant for this membership"
    )

    role_name = forms.ChoiceField(
        label="Role",
        required=True,
        help_text="Select a role (the system will use the role from the selected tenant)"
    )

    class Meta:
        model = TenantMembership
        fields = ['user', 'tenant', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get unique system role names
        system_roles = ['Owner', 'Admin', 'Manager', 'Staff', 'Viewer']
        role_choices = [('', '---------')] + [(name, name) for name in system_roles]
        self.fields['role_name'].choices = role_choices

        # Pre-populate from instance
        if self.instance.pk and self.instance.tenant_id:
            try:
                self.initial['tenant'] = Tenant.objects.get(id=self.instance.tenant_id)
                if self.instance.tenant_role:
                    self.initial['role_name'] = self.instance.tenant_role.name
            except Tenant.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        tenant = cleaned_data.get('tenant')
        role_name = cleaned_data.get('role_name')

        if tenant and role_name:
            # Find the role with this name for the selected tenant
            from tenants_core.rbac.models import TenantRole
            tenant_role = TenantRole.objects.filter(
                tenant_id=tenant.id,
                name=role_name,
                is_active=True
            ).first()

            if not tenant_role:
                raise forms.ValidationError({
                    'role_name': f'Role "{role_name}" does not exist for tenant "{tenant.name}".'
                })

            # Store the found role for save()
            cleaned_data['tenant_role'] = tenant_role

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set tenant_id from selected tenant
        if 'tenant' in self.cleaned_data:
            instance.tenant_id = self.cleaned_data['tenant'].id
        # Set tenant_role from cleaned data
        if 'tenant_role' in self.cleaned_data:
            instance.tenant_role = self.cleaned_data['tenant_role']
        if commit:
            instance.save()
        return instance

# NOTE: User model is NOT registered with default admin.site for tenant admins
# Only UserProfile (read-only view) is available to tenant admins
# Full User admin (with permissions) is only in public_admin_site
class UserAdmin(BaseUserAdmin):
    """
    Full user admin - only for super admins in public admin.

    Security: Platform staff cannot grant superuser or platform_staff access.
    Only superusers can modify these sensitive fields.
    """
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_platform_staff",
        "is_superuser",
        "created_at"
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_platform_staff",
        "is_superuser",
        "created_at"
    ]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Platform Access",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_platform_staff",
                    "is_superuser",
                ),
                "description": (
                    "<strong>Access Levels:</strong><br>"
                    "• <strong>Active:</strong> User can login<br>"
                    "• <strong>Staff status:</strong> Required for ANY admin access<br>"
                    "• <strong>Platform staff:</strong> Can access platform admin (this site). "
                    "Use Groups below for specific permissions.<br>"
                    "• <strong>Superuser:</strong> Full platform control (use sparingly!)"
                )
            },
        ),
        (
            "Permissions & Groups",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
                "description": (
                    "Use Groups to control what platform staff can do. "
                    "E.g., 'Platform: Tenant Manager' group can create/edit tenants."
                )
            },
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (
            "Access Level",
            {
                "fields": ("is_staff", "is_platform_staff", "is_superuser"),
                "description": (
                    "Choose the access level for this user:<br>"
                    "• Check <strong>Staff status</strong> + <strong>Platform staff</strong> "
                    "for support team members<br>"
                    "• Check <strong>Superuser</strong> only for full platform administrators"
                )
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Security: Platform staff cannot see/edit superuser or platform_staff fields.
        Only superusers can modify these sensitive permissions.
        """
        fieldsets = super().get_fieldsets(request, obj)

        # If user is not a superuser, remove sensitive fields
        if not request.user.is_superuser:
            # Create a modified version of fieldsets without sensitive fields
            safe_fieldsets = []
            for name, options in fieldsets:
                if name == "Platform Access":
                    # Only allow is_active and is_staff for platform staff
                    safe_options = options.copy()
                    safe_options['fields'] = ('is_active', 'is_staff')
                    safe_options['description'] = (
                        "<strong>Access Levels:</strong><br>"
                        "• <strong>Active:</strong> User can login<br>"
                        "• <strong>Staff status:</strong> Required for admin access<br>"
                        "<br><em>Note: Only superusers can grant platform staff or superuser access.</em>"
                    )
                    safe_fieldsets.append((name, safe_options))
                elif name == "Permissions & Groups":
                    # Platform staff cannot edit permissions directly
                    continue
                else:
                    safe_fieldsets.append((name, options))
            return tuple(safe_fieldsets)

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """
        Security: Platform staff cannot modify privilege escalation fields.
        """
        readonly = list(self.readonly_fields)

        # Platform staff cannot change these sensitive fields
        if not request.user.is_superuser:
            readonly.extend(['is_platform_staff', 'is_superuser', 'groups', 'user_permissions'])
            # Cannot modify own account
            if obj and obj.id == request.user.id:
                readonly.extend(['is_active', 'is_staff', 'email'])

        return readonly

    def has_delete_permission(self, request, obj=None):
        """
        Security: Platform staff can delete regular users, but not privileged users.
        """
        # Superusers can delete anyone
        if request.user.is_superuser:
            return super().has_delete_permission(request, obj)

        # Platform staff restrictions
        if not obj:
            # General permission check - allow if user has is_staff
            return request.user.is_staff

        # Cannot delete superusers or other platform staff
        if obj.is_superuser or getattr(obj, 'is_platform_staff', False):
            return False

        # Can delete regular users
        return True

    def has_change_permission(self, request, obj=None):
        """
        Security: Platform staff can edit regular users, but not privileged accounts.
        """
        if not request.user.is_superuser:
            # Cannot edit own account (privilege escalation risk)
            if obj and obj.id == request.user.id:
                return False
            # Cannot edit superusers
            if obj and obj.is_superuser:
                return False
            # Cannot edit other platform staff
            if obj and getattr(obj, 'is_platform_staff', False):
                return False

        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        """
        Platform staff can create new users.
        The fieldsets will prevent them from granting dangerous privileges.
        """
        return request.user.is_staff  # Any staff member (superuser or platform_staff)

    def save_model(self, request, obj, form, change):
        """
        Security: Prevent privilege escalation attempts.
        Platform staff can create/edit users but cannot grant elevated privileges.
        """
        # Superusers can do anything
        if request.user.is_superuser:
            super().save_model(request, obj, form, change)
            return

        # Platform staff: Force dangerous flags to False
        # This prevents privilege escalation even if they manipulate the form
        if not request.user.is_superuser:
            original_platform_staff = obj.is_platform_staff
            original_superuser = obj.is_superuser

            # Force these flags to False for platform staff
            obj.is_platform_staff = False
            obj.is_superuser = False

            # If they attempted to set these flags, show a warning
            if change and (original_platform_staff or original_superuser):
                from django.contrib import messages
                messages.warning(
                    request,
                    "Note: Only superusers can grant platform staff or superuser privileges. "
                    "User saved without elevated privileges."
                )

        super().save_model(request, obj, form, change)


@admin.register(User)
class UserProfileAdmin(BaseUserAdmin):
    """
    Simplified user admin for tenant admins.

    Tenant admins can:
    - View users in their tenant
    - Create new users (basic info only)
    - Edit basic user info (name, email)

    They CANNOT:
    - Assign permissions directly
    - Change is_staff, is_superuser
    - Edit groups or user_permissions

    To grant permissions, they must:
    1. Create roles in "Tenant Roles"
    2. Assign roles via "Team Members" (TenantMembership)
    """
    list_display = ["email", "full_name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Status", {"fields": ("is_active",)}),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        ("Important Dates", {
            "fields": ("last_login", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name"),
        }),
    )

    def get_queryset(self, request):
        """Filter to only show users in current tenant."""
        qs = super().get_queryset(request)
        tenant = getattr(connection, 'tenant', None)
        if tenant:
            # Get user IDs that have membership in this tenant
            member_user_ids = TenantMembership.objects.filter(
                tenant_id=tenant.id
            ).values_list('user_id', flat=True)
            return qs.filter(id__in=member_user_ids)
        return qs.none()

    def full_name(self, obj):
        """Display full name."""
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "-"
    full_name.short_description = "Name"

    def get_readonly_fields(self, request, obj=None):
        """Make sensitive fields read-only."""
        readonly = list(self.readonly_fields)

        # Email cannot be changed after creation
        if obj:
            readonly.append('email')

        return readonly

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deleting users from tenant admin.
        Users should be deactivated via TenantMembership instead.
        """
        return False

    def save_model(self, request, obj, form, change):
        """Ensure new users have is_staff=True and create membership."""
        if not change:  # New user
            obj.is_staff = True
        super().save_model(request, obj, form, change)

        # Create membership for new user
        if not change:
            tenant = getattr(connection, 'tenant', None)
            if tenant:
                # Check if membership already exists
                if not TenantMembership.objects.filter(
                    user=obj,
                    tenant_id=tenant.id
                ).exists():
                    # Get default role (Member or first available role)
                    from tenants_core.rbac.models import TenantRole
                    default_role = TenantRole.objects.filter(
                        tenant_id=tenant.id,
                        is_active=True,
                        is_system=True,
                        name='Member'
                    ).first()

                    if not default_role:
                        # Fallback to first active role
                        default_role = TenantRole.objects.filter(
                            tenant_id=tenant.id,
                            is_active=True
                        ).first()

                    if default_role:
                        TenantMembership.objects.create(
                            user=obj,
                            tenant_id=tenant.id,
                            tenant_role=default_role,
                            is_active=True
                        )


# TenantMembership is NOT registered with default admin.site for tenants
# This prevents tenant admins from editing their own roles
# Only available in public_admin_site for super admins
class TenantMembershipAdmin(admin.ModelAdmin):
    """Full membership admin - only for super admins in public admin."""
    form = TenantMembershipAdminForm
    list_display = ["user", "tenant_display", "role_display", "is_active", "joined_at"]
    list_filter = ["is_active", "joined_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["joined_at", "updated_at"]
    autocomplete_fields = ["user"]

    fieldsets = (
        ("Membership", {
            "fields": ("user", "tenant", "role_name", "is_active"),
            "description": "Select the tenant and role name. The system will use the correct role for that tenant."
        }),
        ("Timestamps", {
            "fields": ("joined_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def tenant_display(self, obj):
        """Display tenant name and domain."""
        try:
            tenant = Tenant.objects.get(id=obj.tenant_id)
            return f"{tenant.name} ({tenant.primary_domain})"
        except Tenant.DoesNotExist:
            return str(obj.tenant_id)
    tenant_display.short_description = "Tenant"

    def role_display(self, obj):
        """Display role name."""
        if obj.tenant_role:
            return obj.tenant_role.name
        return obj.role  # Fallback to legacy role field
    role_display.short_description = "Role"
    role_display.admin_order_field = "tenant_role__name"
@admin.register(TenantMembership)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Team Members admin for tenant admins.

    This allows tenant admins to:
    - View their team members
    - Assign roles to team members
    - Activate/deactivate memberships

    Security measures:
    - Filters to only show current tenant's members
    - Cannot edit own membership (prevents role escalation)
    - Can only assign roles that exist for the tenant
    - Cannot change tenant_id
    """
    list_display = ["user_email", "user_name", "role_display", "is_active", "joined_at"]
    list_filter = ["is_active", "joined_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["joined_at", "updated_at"]
    ordering = ["-joined_at"]

    fieldsets = (
        ("Team Member", {
            "fields": ("user", "tenant_role", "is_active")
        }),
        ("Timestamps", {
            "fields": ("joined_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def get_queryset(self, request):
        """Filter to only show current tenant's memberships."""
        from django.db import connection
        qs = super().get_queryset(request)
        tenant = getattr(connection, 'tenant', None)
        if tenant:
            return qs.filter(tenant_id=tenant.id).select_related('user', 'tenant_role')
        return qs.none()

    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = "Email"
    user_email.admin_order_field = "user__email"

    def user_name(self, obj):
        """Display user name."""
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name if name else "-"
    user_name.short_description = "Name"

    def role_display(self, obj):
        """Display role name."""
        if obj.tenant_role:
            return obj.tenant_role.name
        return obj.role  # Fallback to legacy role field
    role_display.short_description = "Role"
    role_display.admin_order_field = "tenant_role__name"

    def get_readonly_fields(self, request, obj=None):
        """Make fields read-only as appropriate."""
        readonly = list(self.readonly_fields)

        # If viewing own membership, make all fields read-only
        if obj and obj.user == request.user:
            return ['user', 'tenant_role', 'is_active', 'joined_at', 'updated_at']

        # Cannot change user after creation
        if obj:
            readonly.append('user')

        return readonly

    def has_add_permission(self, request):
        """
        Prevent adding new memberships from tenant admin.
        Memberships should be created when users are created.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Allow viewing own membership (read-only via get_readonly_fields).
        Prevent editing own membership to avoid role escalation.
        """
        # List view - show all memberships
        if obj is None:
            return super().has_change_permission(request, obj)

        # Can view own membership (readonly) or edit others
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Prevent users from deleting their own membership."""
        if obj and obj.user == request.user:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        """Auto-set tenant_id from current tenant."""
        from django.db import connection
        if not obj.tenant_id:
            tenant = getattr(connection, 'tenant', None)
            if tenant:
                obj.tenant_id = tenant.id
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter tenant_role to only show roles for current tenant."""
        if db_field.name == "tenant_role":
            from tenants_core.rbac.models import TenantRole
            tenant = getattr(connection, 'tenant', None)
            if tenant:
                kwargs["queryset"] = TenantRole.objects.filter(
                    tenant_id=tenant.id,
                    is_active=True
                ).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
