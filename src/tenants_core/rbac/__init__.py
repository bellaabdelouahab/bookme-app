"""
Role-Based Access Control (RBAC) for multi-tenant system.

This module provides tenant-scoped role and permission management:
- TenantRole model in SHARED schema
- Automatic tenant_id scoping to prevent cross-tenant access
- System roles (Owner, Admin, Manager, Staff, Viewer)
- Custom role creation per tenant
- Permission backend integration
"""
