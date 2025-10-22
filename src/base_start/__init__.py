"""
Base Start - Template apps for tenant schemas.

This package serves as a TEMPLATE for creating tenant-specific schemas.
When a tenant is created and selects an app_type (SALON, CLINIC, GYM, etc.),
these apps are instantiated in the tenant's PostgreSQL schema.

Available apps:
- bookings: Appointment and booking management
- communications: Email, SMS, and notification templates
- customers: Customer/client management
- payments: Payment processing and invoicing
- resources: Room, equipment, and resource management
- services: Service catalog and pricing
- staff: Staff member management and scheduling

Each tenant gets their own isolated copy of these tables in their schema.
"""
