"""
Admin interface for RBAC (Role-Based Access Control).

Provides tenant-scoped role management in the Django admin.
"""
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.db import connection
from django.utils.html import format_html
from .models import TenantRole


class TenantRoleAdminForm(forms.ModelForm):
    """
    Custom form for TenantRole admin with permission selection widget.
    """
    # Allowed app labels for tenant role permissions
    ALLOWED_APP_LABELS = [
        'services',     # Services
        'staff',        # Staff management
        'customers',    # Customer management
        'bookings',     # Booking management
        'communications', # Notifications
        'payments',     # Payments
        'resources',    # Resources
    ]

    # Excluded permissions (even from allowed apps)
    EXCLUDED_PERMISSIONS = [
        # User-related (managed via Team Members admin)
        'add_user', 'change_user', 'delete_user',
        # Membership management (prevents role escalation)
        'add_tenantmembership', 'change_tenantmembership', 'delete_tenantmembership',
        # Role management (only Owner should manage roles)
        'add_tenantrole', 'change_tenantrole', 'delete_tenantrole',
    ]

    class Meta:
        model = TenantRole
        fields = ['name', 'description', 'is_active', 'metadata']
        exclude = ['permissions', 'tenant_id', 'is_system', 'role_type']
        # Exclude the JSONField 'permissions' - we handle it with custom field in __init__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add permissions field as a custom field
        self.fields['permissions'] = forms.ModelMultipleChoiceField(
            queryset=Permission.objects.filter(
                content_type__app_label__in=self.ALLOWED_APP_LABELS
            ).exclude(
                codename__in=self.EXCLUDED_PERMISSIONS
            ).select_related('content_type').order_by('content_type__app_label', 'codename'),
            required=False,
            widget=admin.widgets.FilteredSelectMultiple(
                verbose_name='Permissions',
                is_stacked=False
            ),
            help_text='Select the permissions this role should grant to users.'
        )

        # If editing existing role, pre-select permissions from JSONField
        if self.instance.pk and self.instance.permissions:
            permission_codenames = self.instance.permissions
            self.initial['permissions'] = Permission.objects.filter(
                codename__in=permission_codenames
            )

        # Auto-populate tenant_id from current tenant
        tenant = getattr(connection, 'tenant', None)
        if tenant and not self.instance.pk:
            self.initial['tenant_id'] = tenant.id

        # Make system roles read-only
        if self.instance.pk and self.instance.is_system:
            # Make all fields disabled for system roles
            for field_name in self.fields:
                self.fields[field_name].disabled = True
            # Add warning message to description field instead of name
            if 'description' in self.fields:
                current_help = self.fields['description'].help_text or ''
                self.fields['description'].help_text = (
                    f'⚠️ This is a system role. All fields are read-only. {current_help}'
                )

    def clean(self):
        cleaned_data = super().clean()

        # Remove 'permissions' from cleaned_data to prevent JSON validation
        # We'll handle it manually in save()
        if 'permissions' in cleaned_data:
            # Store it temporarily so save() can access it
            self._selected_permissions = cleaned_data['permissions']

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Convert Permission objects to permission codenames for JSONField
        # Use the stored permissions from clean()
        if hasattr(self, '_selected_permissions'):
            selected_permissions = self._selected_permissions
            if selected_permissions:
                instance.permissions = [
                    perm.codename for perm in selected_permissions
                ]
            else:
                instance.permissions = []
        elif 'permissions' in self.cleaned_data:
            selected_permissions = self.cleaned_data['permissions']
            if selected_permissions:
                instance.permissions = [
                    perm.codename for perm in selected_permissions
                ]
            else:
                instance.permissions = []
        else:
            # If no permissions were selected, set empty list
            instance.permissions = []

        if commit:
            instance.save()

        return instance


class TenantRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for TenantRole model.

    Features:
    - Automatically filters roles by current tenant
    - Prevents editing/deletion of system roles
    - Shows permission count and status
    - Provides permission selection widget
    """
    form = TenantRoleAdminForm
    list_display = [
        'name',
        'role_type',
        'permission_count',
        'is_system_badge',
        'is_active_badge',
        'created_at',
    ]
    list_filter = ['role_type', 'is_system', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'tenant_id_display']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'description': 'Select the permissions this role should grant to users.'
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Additional Configuration', {
            'fields': ('metadata',),
            'classes': ('collapse',),
            'description': 'Advanced role configuration (JSON format).'
        }),
        ('Metadata', {
            'fields': ('id', 'tenant_id_display', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """
        Filter roles to only show current tenant's roles.
        """
        qs = super().get_queryset(request)
        tenant = getattr(connection, 'tenant', None)
        if tenant:
            return qs.filter(tenant_id=tenant.id)
        return qs.none()

    def tenant_id_display(self, obj):
        """Display tenant_id in read-only format."""
        if obj.tenant_id:
            return format_html(
                '<code>{}</code>',
                str(obj.tenant_id)
            )
        return '-'
    tenant_id_display.short_description = 'Tenant ID'

    def permission_count(self, obj):
        """Display count of permissions assigned to this role."""
        count = len(obj.permissions or [])
        if count == 0:
            return format_html('<span style="color: #999;">0 permissions</span>')
        return format_html(
            '<strong>{}</strong> permission{}',
            count,
            's' if count != 1 else ''
        )
    permission_count.short_description = 'Permissions'

    def is_system_badge(self, obj):
        """Display badge for system roles."""
        if obj.is_system:
            return format_html(
                '<span style="background: #417690; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">SYSTEM</span>'
            )
        return format_html(
            '<span style="color: #666; font-size: 11px;">Custom</span>'
        )
    is_system_badge.short_description = 'Type'

    def is_active_badge(self, obj):
        """Display badge for active status."""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">●</span> Active'
            )
        return format_html(
            '<span style="color: #dc3545;">●</span> Inactive'
        )
    is_active_badge.short_description = 'Status'

    def has_module_permission(self, request):
        """
        Check if user has permission to see the RBAC module in admin.
        """
        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if user has any RBAC-related permission
        return (
            request.user.has_perm('rbac.view_tenantrole') or
            request.user.has_perm('rbac.add_tenantrole') or
            request.user.has_perm('rbac.change_tenantrole') or
            request.user.has_perm('rbac.delete_tenantrole')
        )

    def has_view_permission(self, request, obj=None):
        """
        Check if user can view TenantRole in admin.
        """
        if request.user.is_superuser:
            return True
        return request.user.has_perm('rbac.view_tenantrole')

    def has_change_permission(self, request, obj=None):
        """
        Allow viewing system roles but show save button disabled via readonly fields.
        """
        # Allow viewing in list and detail (readonly)
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of system roles.
        """
        if obj and obj.is_system:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        """
        Ensure tenant_id is set from current tenant context.
        Prevent creating system roles via admin (only custom roles allowed).
        """
        if not obj.tenant_id:
            tenant = getattr(connection, 'tenant', None)
            if tenant:
                obj.tenant_id = tenant.id

        # Ensure custom roles created via admin are never system roles
        if not change:  # New role
            obj.is_system = False
            obj.role_type = 'custom'

        # Prevent modification of system roles
        if obj.is_system and change:
            return  # Don't save changes to system roles

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """
        Make additional fields read-only for system roles.
        """
        readonly = list(self.readonly_fields)

        # Make all fields read-only for system roles (view only)
        if obj and obj.is_system:
            readonly.extend(['name', 'description', 'permissions', 'is_active', 'metadata'])

        return readonly


# Register with the tenant admin site
admin.site.register(TenantRole, TenantRoleAdmin)
