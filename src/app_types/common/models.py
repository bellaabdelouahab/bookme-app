"""
Abstract base models for app types.

These provide common fields and methods that all business-specific models inherit.
Each app type (salon, clinic, gym) extends these with their specific fields.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from tenants_core.core.models import TenantAwareModel


class BaseBooking(TenantAwareModel):
    """
    Abstract base for all booking/appointment models.

    Provides common fields shared across salon bookings, clinic appointments,
    gym sessions, restaurant reservations, etc.

    Business-specific apps extend this with their own fields.
    """
    # Universal booking fields
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
        help_text=_("Customer making the booking")
    )

    booking_date = models.DateField(
        help_text=_("Date of the booking/appointment")
    )
    start_time = models.TimeField(
        help_text=_("Start time")
    )
    end_time = models.TimeField(
        help_text=_("End time")
    )

    # Status tracking
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        CHECKED_IN = 'checked_in', _('Checked In')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        NO_SHOW = 'no_show', _('No Show')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Common metadata
    notes = models.TextField(
        blank=True,
        help_text=_("Internal notes about this booking")
    )
    customer_notes = models.TextField(
        blank=True,
        help_text=_("Notes from the customer")
    )

    # Cancellation tracking
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    cancellation_reason = models.TextField(
        blank=True
    )

    class Meta:
        abstract = True
        ordering = ['booking_date', 'start_time']
        indexes = [
            models.Index(fields=['booking_date', 'start_time']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        """Validate booking times."""
        super().clean()
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError({
                    'end_time': _('End time must be after start time')
                })

    def get_duration_minutes(self):
        """Calculate booking duration in minutes."""
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(self.booking_date, self.start_time)
            end = datetime.combine(self.booking_date, self.end_time)
            return int((end - start).total_seconds() / 60)
        return 0

    def can_cancel(self):
        """Check if booking can be cancelled."""
        return self.status in [
            self.Status.PENDING,
            self.Status.CONFIRMED
        ]

    def __str__(self):
        return f"{self.customer} - {self.booking_date} {self.start_time}"


class BaseService(TenantAwareModel):
    """
    Abstract base for service/offering models.

    Common fields for hair services, medical services, gym classes,
    restaurant menu items, etc.
    """
    name = models.CharField(
        max_length=200,
        help_text=_("Service name")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description")
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Base price for this service")
    )

    # Duration
    duration_minutes = models.PositiveIntegerField(
        help_text=_("Typical duration in minutes")
    )

    # Availability
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this service is currently offered")
    )

    # Display order
    display_order = models.PositiveIntegerField(
        default=0,
        help_text=_("Order to display in lists (lower = first)")
    )

    class Meta:
        abstract = True
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class BaseStaffMember(TenantAwareModel):
    """
    Abstract base for staff/provider models.

    Common fields for stylists, doctors, trainers, waitstaff, etc.
    """
    # Link to user account
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_profile',
        help_text=_("Associated user account")
    )

    # Basic info
    display_name = models.CharField(
        max_length=100,
        help_text=_("Name shown to customers")
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Professional title (e.g., 'Senior Stylist', 'MD', 'Personal Trainer')")
    )
    bio = models.TextField(
        blank=True,
        help_text=_("Professional biography")
    )

    # Contact
    phone = models.CharField(
        max_length=20,
        blank=True
    )
    email = models.EmailField(
        blank=True
    )

    # Availability
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this staff member is currently active")
    )
    accepts_bookings = models.BooleanField(
        default=True,
        help_text=_("Whether customers can book with this staff member")
    )

    # Display
    profile_photo = models.ImageField(
        upload_to='staff_photos/',
        blank=True,
        null=True
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text=_("Order to display in lists")
    )

    class Meta:
        abstract = True
        ordering = ['display_order', 'display_name']

    def __str__(self):
        if self.title:
            return f"{self.display_name}, {self.title}"
        return self.display_name


class BaseCategory(TenantAwareModel):
    """
    Abstract base for categorization models.

    Used to organize services, menu items, workout plans, etc.
    """
    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text=_("Parent category for hierarchical organization")
    )
    display_order = models.PositiveIntegerField(
        default=0
    )
    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        abstract = True
        ordering = ['display_order', 'name']
        verbose_name_plural = _('categories')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
