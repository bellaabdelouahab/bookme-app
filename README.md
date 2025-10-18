# BookMe.ma - Multi-Tenant Booking Platform

A production-ready, scalable multi-tenant booking management platform built with Django, PostgreSQL schema isolation, and modern DevOps practices.

## 🏗️ Architecture

- **Pattern**: Modular Monolith (easily extractable to microservices)
- **Multi-Tenancy**: Schema-per-tenant using PostgreSQL schemas
- **Database**: PostgreSQL 16 with tenant isolation
- **Cache/Queue**: Redis for caching and Celery broker
- **API**: Django REST Framework with JWT authentication
- **Task Queue**: Celery with Beat scheduler
- **Containerization**: Docker with multi-stage builds

## 📋 Features

- ✅ **Multi-Tenant System**: Full schema isolation per tenant
- ✅ **Service Management**: Flexible service catalog with metadata
- ✅ **Staff Management**: Staff scheduling and availability
- ✅ **Customer Management**: Customer profiles with consent tracking
- ✅ **Booking System**: Appointment booking with status tracking
- ✅ **Communications**: Multi-channel notifications (SMS, WhatsApp, Email)
- ✅ **Payments**: Integrated payment processing
- ✅ **API Documentation**: Swagger/ReDoc with drf-spectacular
- ✅ **Background Jobs**: Celery for async tasks
- ✅ **Monitoring**: Structured logging, Sentry integration
- ✅ **Testing**: Pytest with factory-boy and coverage

## 📚 Documentation

- **[Tenant Architecture Guide](docs/TENANT_GUIDE.md)** - Complete guide to multi-tenant architecture
- **[Quick Reference Cheat Sheet](docs/CHEAT_SHEET.md)** - Quick commands and patterns
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Database migration workflow
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed installation instructions
- **[Architecture Overview](docs/architecture/modular-monolith.md)** - System design principles

## 🚀 Quick Start

### Prerequisites

- Python 3.11 (pyenv-win recommended for version management on Windows)
- Docker & Docker Compose
- PostgreSQL 16 (if running locally)
- Redis 7 (if running locally)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bookme.ma.git
   cd bookme.ma
   ```

2. **Create environment file**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up Python environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -e ".[dev]"
   ```

4. **Start database services**
   ```bash
   docker-compose up -d db redis
   ```

5. **Run migrations**
   ```bash
   cd src
   python manage.py migrate_schemas --shared   # Shared schema
   python manage.py migrate_schemas            # All tenant schemas
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create your first tenant**
   ```bash
   python manage.py shell
   ```
   ```python
   from bookme.tenant.models import Tenant, Domain

   tenant = Tenant.objects.create(
       schema_name='tenant_demo',
       name='Demo Company',
       primary_domain='demo.localhost',
       contact_email='demo@test.com',
       status='active'
   )

   Domain.objects.create(
       domain='demo.localhost',
       tenant=tenant,
       is_primary=True
   )
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Public API: http://localhost:8000/api/
   - Tenant API: http://demo.localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/schema/swagger/

### 🆕 New to Multi-Tenancy?

Check out our comprehensive guides:
- 📖 **[Tenant Guide](docs/TENANT_GUIDE.md)** - Start here to understand multi-tenancy
- ⚡ **[Cheat Sheet](docs/CHEAT_SHEET.md)** - Quick commands and examples
- 🔄 **[Migration Guide](docs/MIGRATION_GUIDE.md)** - How to update the database

## 📦 Project Structure

```
bookme.ma/
├── src/
│   ├── manage.py
│   └── bookme/
│       ├── __init__.py
│       ├── settings/           # Environment-based settings
│       │   ├── base.py
│       │   ├── local.py
│       │   ├── production.py
│       │   └── test.py
│       ├── urls.py             # Tenant URLs
│       ├── urls_public.py      # Public URLs
│       ├── wsgi.py
│       ├── asgi.py
│       ├── celery.py
│       ├── core/               # Shared utilities
│       │   ├── models.py       # Base models
│       │   ├── middleware.py
│       │   ├── pagination.py
│       │   └── exceptions.py
│       ├── tenant/             # Tenant management
│       │   ├── models.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   └── admin.py
│       ├── users/              # Authentication & Users
│       ├── services/           # Service catalog
│       ├── staff/              # Staff management
│       ├── customers/          # Customer management
│       ├── bookings/           # Booking system
│       ├── communications/     # Notifications
│       ├── payments/           # Payment processing
│       └── resources/          # Resources & media
├── tests/                      # Test suite
├── docs/                       # Documentation
│   ├── architecture/
│   └── uml/
├── scripts/                    # Utility scripts
├── nginx/                      # Nginx configuration
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production
├── Dockerfile                  # Multi-stage build
├── pyproject.toml             # Python dependencies
├── .env.example               # Environment template
└── README.md
```

## 🛠️ Development

### Local Setup (without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up database**
   ```bash
   createdb bookme
   python src/manage.py migrate_schemas --shared
   ```

4. **Run development server**
   ```bash
   python src/manage.py runserver
   ```

5. **Run Celery worker** (in another terminal)
   ```bash
   celery -A bookme worker --loglevel=info
   ```

6. **Run Celery beat** (in another terminal)
   ```bash
   celery -A bookme beat --loglevel=info
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tenant.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Database Migrations

```bash
# Create migration for shared apps
python src/manage.py makemigrations

# Apply migrations to public schema
python src/manage.py migrate_schemas --shared

# Apply migrations to all tenant schemas
python src/manage.py migrate_schemas

# Create a new tenant
python src/manage.py create_tenant
```

## 🏢 Multi-Tenant Usage

### Creating a Tenant

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/tenants/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Business",
    "subdomain": "mybusiness",
    "contact_email": "admin@mybusiness.com",
    "contact_phone": "+212600000000"
  }'
```

**Via Management Command:**
```bash
python src/manage.py create_tenant \
  --name "My Business" \
  --schema mybusiness \
  --domain mybusiness.bookme.ma
```

### Accessing Tenant

Each tenant is accessed via their subdomain:
- Tenant 1: `https://tenant1.bookme.ma`
- Tenant 2: `https://tenant2.bookme.ma`

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Obtain Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'
```

### Use Token

```bash
curl -X GET http://localhost:8000/api/v1/bookings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## 🚢 Deployment

### Production Deployment

1. **Set environment variables**
   ```bash
   # See .env.example for all variables
   export DJANGO_SETTINGS_MODULE=bookme.settings.production
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=postgres://user:pass@host:5432/bookme
   export REDIS_URL=redis://host:6379/0
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web \
     python src/manage.py migrate_schemas --shared
   ```

4. **Collect static files**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web \
     python src/manage.py collectstatic --noinput
   ```

### SSL Certificates

```bash
# Generate SSL certificate with Certbot
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d bookme.ma -d www.bookme.ma
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `bookme.settings.local` |
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | PostgreSQL connection | - |
| `REDIS_URL` | Redis connection | - |
| `CELERY_BROKER_URL` | Celery broker | Same as REDIS_URL |
| `ALLOWED_HOSTS` | Allowed hosts | `[]` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `[]` |
| `SENTRY_DSN` | Sentry DSN | - |

### Tenant Configuration

Tenants can be configured via the `TenantConfig` model:

```python
from bookme.tenant.models import TenantConfig

# Set branding
TenantConfig.objects.create(
    tenant=my_tenant,
    category="branding",
    key="primary_color",
    value={"color": "#007bff"}
)

# Set feature flags
TenantConfig.objects.create(
    tenant=my_tenant,
    category="features",
    key="online_payments",
    value={"enabled": True}
)
```

## 📈 Monitoring & Observability

### Logging

Structured logging with request context:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Booking created", extra={
    "booking_id": booking.id,
    "tenant_id": tenant.id,
    "customer_id": customer.id
})
```

### Sentry Integration

Automatic error tracking with Sentry:
```python
# Configure in .env
SENTRY_DSN=your-sentry-dsn
SENTRY_ENVIRONMENT=production
```

### Celery Monitoring

Access Flower dashboard:
- URL: http://localhost:5555
- Monitor tasks, workers, and queues

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_tenant.py           # Tenant tests
├── test_services.py         # Service tests
├── test_bookings.py         # Booking tests
└── factories/               # Factory Boy factories
    ├── tenant.py
    ├── services.py
    └── bookings.py
```

### Writing Tests

```python
import pytest
from tests.factories import TenantFactory, ServiceFactory

@pytest.mark.django_db
def test_create_service(tenant):
    service = ServiceFactory(tenant=tenant)
    assert service.name
    assert service.price > 0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use Black for formatting
- Use Ruff for linting
- Add type hints where possible
- Write docstrings for all public methods

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework teams
- django-tenants for multi-tenancy support
- All open-source contributors

## 📞 Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/bookme.ma/issues)
- **Email**: dev@bookme.ma

---

**Built with ❤️ for the Moroccan market**
