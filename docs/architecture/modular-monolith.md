# Modular Monolith Architecture

## Structure
```
bookme.ma/
├── apps/
│   ├── api/           # Single API server
│   └── web/           # Customer booking frontend
│   └── admin/         # Tenant admin dashboard
├── packages/
│   ├── tenant/        # Tenant management module
│   ├── booking/       # Booking core module
│   ├── staff/         # Staff & services module
│   ├── customer/      # Customer module
│   ├── communications/# Notifications module
│   ├── payments/      # Payment processing module
│   └── shared/        # Common utilities
└── infrastructure/
    ├── database/      # Schema management, migrations
    └── queue/         # Background jobs (optional)
```

## Module Boundaries
- Each package is independently testable
- Modules communicate via well-defined interfaces
- No direct database access between modules
- Easy to extract into microservices later

## When to Consider Microservices Later:

### Trigger Points:
1. **Scale**: >10,000 tenants or >1M bookings/month
2. **Team Size**: >15 developers
3. **Independent Scaling**: Communications module needs 10x more resources
4. **Third-party Integration**: Payment provider requires isolation
5. **Regulatory**: Payment data must be physically separated

### Easy Migration Path:
Your current design supports this:
- `tenantId` in every table (already partitioned)
- Event log (`BookingEvent`) can become event stream
- JSON metadata fields avoid schema dependencies
- Module structure maps to services
```
