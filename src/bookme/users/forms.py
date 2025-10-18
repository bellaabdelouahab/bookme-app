"""Admin forms for users and memberships."""
from django import forms

from bookme.tenant.models import Tenant

from .models import TenantMembership


class TenantMembershipAdminForm(forms.ModelForm):
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all().order_by("name"),
        required=True,
        help_text="Select the tenant to link this user to.",
        label="Tenant",
    )

    class Meta:
        model = TenantMembership
        fields = [
            "user",
            "tenant",  # virtual field maps to tenant_id
            "role",
            "permissions",
            "is_active",
            "metadata",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate tenant dropdown from instance.tenant_id when editing
        if self.instance and self.instance.pk and self.instance.tenant_id:
            try:
                self.fields["tenant"].initial = Tenant.objects.get(id=self.instance.tenant_id)
            except Tenant.DoesNotExist:
                pass

    def save(self, commit=True):
        obj = super().save(commit=False)
        tenant_obj = self.cleaned_data.get("tenant")
        if tenant_obj:
            obj.tenant_id = tenant_obj.id
        if commit:
            obj.save()
        return obj
