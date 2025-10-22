"""
Module registry for tenant app configuration.

This module defines all available modules that can be enabled/disabled per tenant.
It provides a centralized way to manage which features are available for different
business types.
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Module:
    """
    Represents a feature module that can be enabled for a tenant.

    Attributes:
        name: Unique identifier for the module
        label: Human-readable name
        apps: List of Django apps included in this module
        description: What this module provides
        required: If True, module cannot be disabled
        icon: Icon class/name for UI (optional)
    """
    name: str
    label: str
    apps: List[str]
    description: str
    required: bool = False
    icon: str = ""


# Registry of all available modules
AVAILABLE_MODULES: Dict[str, Module] = {
    'bookings': Module(
        name='bookings',
        label='Booking Management',
        apps=['base_start.bookings'],
        description='Appointment and reservation scheduling system',
        required=True,  # Core module - required for all tenants
        icon='calendar'
    ),
    'customers': Module(
        name='customers',
        label='Customer Management',
        apps=['base_start.customers'],
        description='Customer database, profiles, and history tracking',
        required=True,  # Core module - required for all tenants
        icon='users'
    ),
    'communications': Module(
        name='communications',
        label='Communications',
        apps=['base_start.communications'],
        description='SMS, email notifications, and messaging',
        required=True,  # Core module - required for all tenants
        icon='mail'
    ),
    'staff': Module(
        name='staff',
        label='Staff Management',
        apps=['base_start.staff'],
        description='Staff members, scheduling, and availability management',
        required=False,
        icon='user-check'
    ),
    'services': Module(
        name='services',
        label='Service Catalog',
        apps=['base_start.services'],
        description='Service offerings, pricing, and packages',
        required=False,
        icon='grid'
    ),
    'payments': Module(
        name='payments',
        label='Payment Processing',
        apps=['base_start.payments'],
        description='Payment processing, invoicing, and billing',
        required=False,
        icon='dollar-sign'
    ),
    'resources': Module(
        name='resources',
        label='Resource Management',
        apps=['base_start.resources'],
        description='Rooms, equipment, inventory, and asset tracking',
        required=False,
        icon='package'
    ),
}


def get_module(name: str) -> Module:
    """
    Get module by name.

    Args:
        name: Module identifier

    Returns:
        Module instance

    Raises:
        KeyError: If module doesn't exist
    """
    return AVAILABLE_MODULES[name]


def get_required_modules() -> List[str]:
    """
    Get list of required module names.

    Returns:
        List of module names that are required
    """
    return [
        name for name, module in AVAILABLE_MODULES.items()
        if module.required
    ]


def get_optional_modules() -> List[str]:
    """
    Get list of optional module names.

    Returns:
        List of module names that are optional
    """
    return [
        name for name, module in AVAILABLE_MODULES.items()
        if not module.required
    ]


def validate_modules(modules: Dict[str, bool]) -> tuple[bool, List[str]]:
    """
    Validate module configuration.

    Args:
        modules: Dict of module names to enabled status

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check all required modules are enabled
    for required_module in get_required_modules():
        if not modules.get(required_module, False):
            errors.append(f"Required module '{required_module}' must be enabled")

    # Check for unknown modules
    for module_name in modules.keys():
        if module_name not in AVAILABLE_MODULES:
            errors.append(f"Unknown module: '{module_name}'")

    return (len(errors) == 0, errors)


def get_all_module_apps() -> List[str]:
    """
    Get list of all Django apps from all modules.

    Returns:
        List of Django app paths
    """
    apps = []
    for module in AVAILABLE_MODULES.values():
        apps.extend(module.apps)
    return list(set(apps))  # Remove duplicates
