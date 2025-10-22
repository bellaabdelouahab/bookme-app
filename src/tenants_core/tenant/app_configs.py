"""
App-type specific configuration for tenant modules.

Defines which modules are enabled by default for each business type.
"""
from typing import Dict, List
from tenants_core.core.modules import get_required_modules


# Default module configuration for each app type
APP_TYPE_MODULE_CONFIGS: Dict[str, Dict[str, any]] = {
    'salon': {
        'enabled_modules': [
            'bookings',          # Required - appointment scheduling
            'customers',         # Required - customer database
            'communications',    # Required - SMS/email notifications
            'staff',             # Staff management and scheduling
            'services',          # Service catalog (haircuts, coloring, etc.)
            'payments',          # Payment processing
            'resources',         # Inventory (products, tools)
        ],
        'default_features': {
            'online_booking': True,
            'inventory_management': True,
            'loyalty_program': True,
            'pos_system': False,
        },
        'description': 'Hair salon / Barbershop with staff scheduling and inventory',
    },
    'clinic': {
        'enabled_modules': [
            'bookings',          # Required - appointment scheduling
            'customers',         # Required - patient database
            'communications',    # Required - appointment reminders
            'staff',             # Doctor/nurse scheduling
            'services',          # Medical services catalog
            'payments',          # Billing and payments
            # NOTE: No 'resources' - clinics typically don't need inventory tracking
        ],
        'default_features': {
            'online_booking': True,
            'medical_records': True,
            'insurance_billing': True,
            'telehealth': False,
        },
        'description': 'Medical clinic with appointment and patient management',
    },
    'gym': {
        'enabled_modules': [
            'bookings',          # Required - class/session scheduling
            'customers',         # Required - member database
            'communications',    # Required - class reminders
            'staff',             # Trainer/instructor management
            'services',          # Classes, personal training packages
            'payments',          # Membership billing
            'resources',         # Equipment tracking
        ],
        'default_features': {
            'online_booking': True,
            'membership_management': True,
            'class_scheduling': True,
            'equipment_tracking': True,
            'access_control': False,
        },
        'description': 'Gym / Fitness center with class scheduling and memberships',
    },
    'spa': {
        'enabled_modules': [
            'bookings',          # Required - appointment scheduling
            'customers',         # Required - customer database
            'communications',    # Required - appointment confirmations
            'staff',             # Therapist scheduling
            'services',          # Spa services (massage, facial, etc.)
            'payments',          # Payment processing
            'resources',         # Room management, supplies
        ],
        'default_features': {
            'online_booking': True,
            'package_deals': True,
            'gift_certificates': True,
            'loyalty_program': True,
        },
        'description': 'Spa / Wellness center with treatment scheduling',
    },
    'studio': {
        'enabled_modules': [
            'bookings',          # Required - class/session scheduling
            'customers',         # Required - student/client database
            'communications',    # Required - class reminders
            'staff',             # Instructor management
            'services',          # Classes, workshops
            'payments',          # Class payments
            'resources',         # Studio space, equipment
        ],
        'default_features': {
            'online_booking': True,
            'class_scheduling': True,
            'workshop_management': True,
            'video_streaming': False,
        },
        'description': 'Yoga/Dance/Art studio with class scheduling',
    },
    'restaurant': {
        'enabled_modules': [
            'bookings',          # Required - table reservations
            'customers',         # Required - guest database
            'communications',    # Required - reservation confirmations
            'staff',             # Waitstaff scheduling
            'payments',          # Payment processing
            # NOTE: No 'services' or 'resources' - different use case
        ],
        'default_features': {
            'table_reservation': True,
            'online_ordering': False,
            'delivery_management': False,
            'pos_system': False,
        },
        'description': 'Restaurant with table reservation system',
    },
    'custom': {
        'enabled_modules': [
            'bookings',          # Required - basic scheduling
            'customers',         # Required - customer database
            'communications',    # Required - notifications
            # Minimal setup - owner can enable more modules as needed
        ],
        'default_features': {
            'online_booking': True,
        },
        'description': 'Custom business type with minimal modules',
    },
}


def get_default_modules_for_app_type(app_type: str) -> Dict[str, bool]:
    """
    Get default enabled modules for an app type.

    Args:
        app_type: Business type (salon, clinic, gym, etc.)

    Returns:
        Dict mapping module names to enabled status

    Example:
        >>> get_default_modules_for_app_type('salon')
        {'bookings': True, 'customers': True, 'staff': True, ...}
    """
    # Fallback to 'custom' if app_type not found
    config = APP_TYPE_MODULE_CONFIGS.get(app_type, APP_TYPE_MODULE_CONFIGS['custom'])

    # Ensure required modules are always included
    required = get_required_modules()
    enabled = config['enabled_modules']

    # Build dict with all modules from config + required modules
    modules = {}
    for module in set(enabled + required):
        modules[module] = True

    return modules


def get_default_features_for_app_type(app_type: str) -> Dict[str, any]:
    """
    Get default features for an app type.

    Args:
        app_type: Business type

    Returns:
        Dict of feature flags
    """
    config = APP_TYPE_MODULE_CONFIGS.get(app_type, APP_TYPE_MODULE_CONFIGS['custom'])
    return config.get('default_features', {})


def get_app_type_description(app_type: str) -> str:
    """
    Get human-readable description of an app type.

    Args:
        app_type: Business type

    Returns:
        Description string
    """
    config = APP_TYPE_MODULE_CONFIGS.get(app_type, APP_TYPE_MODULE_CONFIGS['custom'])
    return config.get('description', 'Custom business')


def get_available_app_types() -> List[str]:
    """
    Get list of all available app types.

    Returns:
        List of app type keys
    """
    return list(APP_TYPE_MODULE_CONFIGS.keys())


def validate_app_type(app_type: str) -> bool:
    """
    Check if app type is valid.

    Args:
        app_type: Business type to validate

    Returns:
        True if valid, False otherwise
    """
    return app_type in APP_TYPE_MODULE_CONFIGS
