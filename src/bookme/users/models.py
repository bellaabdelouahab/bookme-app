"""
Custom User model and tenant membership.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the primary identifier.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users_user"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        """Return the short name."""
        return self.first_name or self.email


class TenantMembership(models.Model):
    """
    Links users to tenants with specific roles and permissions.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Administrator"
        MANAGER = "manager", "Manager"
        STAFF = "staff", "Staff"
        VIEWER = "viewer", "Viewer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)  # References tenant.Tenant.id
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    permissions = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_tenant_membership"
        unique_together = [["tenant_id", "user"]]
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["tenant_id", "user"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role} ({self.tenant_id})"
