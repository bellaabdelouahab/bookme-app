"""Signals to align user flags with tenant memberships."""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import TenantMembership, User


def _recompute_is_staff(user: User):
    """Sync user.is_staff with membership roles on create/update/delete.

    - Superusers are never downgraded.
    - If user has any active OWNER/ADMIN membership: set is_staff=True.
    - Otherwise: set is_staff=False.
    """
    if user.is_superuser:
        return
    has_admin_like = TenantMembership.objects.filter(
        user=user, role__in=[TenantMembership.Role.OWNER, TenantMembership.Role.ADMIN], is_active=True
    ).exists()
    if has_admin_like and not user.is_staff:
        User.objects.filter(pk=user.pk).update(is_staff=True)
    elif not has_admin_like and user.is_staff:
        User.objects.filter(pk=user.pk).update(is_staff=False)


@receiver(post_save, sender=TenantMembership)
def on_membership_saved(sender, instance: TenantMembership, created, **kwargs):
    _recompute_is_staff(instance.user)


@receiver(post_delete, sender=TenantMembership)
def on_membership_deleted(sender, instance: TenantMembership, **kwargs):
    _recompute_is_staff(instance.user)
