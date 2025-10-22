# Domain Configuration Guide

## Overview

BookMe uses `TENANT_BASE_DOMAIN` to automatically generate tenant subdomains. This setting should be:
- **Development**: `localhost` (supports `subdomain.localhost:8000`)
- **Production**: `bookme.ma` (supports `subdomain.bookme.ma`)

## Environment Configuration

### `.env` File

```bash
# For local development
TENANT_BASE_DOMAIN=localhost
TENANT_AUTO_CREATE_PRIMARY_DOMAIN=True
```

### Settings Flow

The `TENANT_BASE_DOMAIN` setting works as follows:

1. **base.py** sets default based on DEBUG:
   ```python
   TENANT_BASE_DOMAIN = env(
       "TENANT_BASE_DOMAIN",
       default=("localhost" if DEBUG else "bookme.ma")
   )
   ```

2. **.env** can override this:
   ```bash
   TENANT_BASE_DOMAIN=localhost  # Explicit override
   ```

3. **Tenant creation signal** uses it to expand subdomains:
   ```python
   # If admin enters "acme", it becomes "acme.localhost" or "acme.bookme.ma"
   if "." not in primary_domain:
       base = getattr(settings, "TENANT_BASE_DOMAIN", "localhost")
       primary = f"{primary}.{base}"
   ```

## Current Configuration

### Active Domains

```
localhost -> Public (primary)
127.0.0.1 -> Public
asdf.localhost -> abdelouahab bella (primary)
acme.localhost -> acme (primary)
```

### Settings Values

```
DEBUG: True
TENANT_BASE_DOMAIN: localhost
TENANT_AUTO_CREATE_PRIMARY_DOMAIN: True
```

## Common Issues

### Issue: Getting `subdomain.bookme.ma` in Development

**Cause 1**: Wrong path calculation in `settings/base.py` (FIXED)

The path calculation in `settings/base.py` was incorrect, causing the `.env` file to not be found:

```python
# WRONG (was looking for .env in C:\GitHub instead of C:\GitHub\bookme.ma)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

# CORRECT (now finds .env in C:\GitHub\bookme.ma)
BASE_DIR = Path(__file__).resolve().parent.parent  # src/
ROOT_DIR = BASE_DIR.parent  # bookme.ma/
```

**Cause 2**: Existing tenants were created when `TENANT_BASE_DOMAIN=bookme.ma`

**Solution**: Convert existing domains to localhost:

```bash
python manage.py shell -c "
from tenants_core.tenant.models import Domain, Tenant

# Convert .bookme.ma to .localhost
domains = Domain.objects.filter(domain__endswith='.bookme.ma')
for domain in domains:
    old = domain.domain
    domain.domain = old.replace('.bookme.ma', '.localhost')
    domain.save()

    # Update tenant primary_domain
    tenant = domain.tenant
    if tenant.primary_domain == old:
        tenant.primary_domain = domain.domain
        tenant.save()

    print(f'Converted: {old} -> {domain.domain}')
"
```

Or use the management command:

```bash
python manage.py convert_domains_localhost
```

### Issue: New Tenants Still Get `.bookme.ma`

**Check**:
1. Verify `.env` has `TENANT_BASE_DOMAIN=localhost`
2. Restart Django server to pick up env changes
3. Verify in shell:
   ```bash
   python manage.py shell -c "from django.conf import settings; print(settings.TENANT_BASE_DOMAIN)"
   ```

### Issue: Can't Access Tenant Admin

**Verify**:
1. Domain exists in database:
   ```bash
   python manage.py shell -c "from tenants_core.tenant.models import Domain; print(Domain.objects.all())"
   ```

2. Add to hosts file if needed (Windows):
   ```
   C:\Windows\System32\drivers\etc\hosts

   127.0.0.1   subdomain.localhost
   ```

   Note: Modern browsers support `*.localhost` automatically, so this is usually not needed.

3. Check ALLOWED_HOSTS includes wildcard:
   ```python
   # In settings, this is automatic:
   ALLOWED_HOSTS.append('.localhost')
   ```

## Management Commands

### Convert Domains Between localhost and bookme.ma

```bash
# Convert .bookme.ma to .localhost (for local dev)
python manage.py convert_domains_localhost

# Convert back to .bookme.ma (for production deployment)
python manage.py convert_domains_localhost --reverse
```

### List All Domains

```bash
python manage.py shell -c "
from tenants_core.tenant.models import Domain
for d in Domain.objects.all():
    print(f'{d.domain} -> {d.tenant.name} (primary={d.is_primary})')
"
```

## Best Practices

### Development Workflow

1. **Set `.env` once**:
   ```bash
   TENANT_BASE_DOMAIN=localhost
   ```

2. **Create tenants with subdomain only**:
   - In admin, enter: `acme` (not `acme.localhost`)
   - Signal auto-expands to: `acme.localhost`

3. **Access tenant**:
   - URL: `http://acme.localhost:8000/admin/`

### Production Deployment

1. **Update `.env`**:
   ```bash
   TENANT_BASE_DOMAIN=bookme.ma
   DEBUG=False
   ```

2. **Convert existing domains**:
   ```bash
   python manage.py convert_domains_localhost --reverse
   ```

3. **DNS Configuration**:
   - Add wildcard A record: `*.bookme.ma -> your-server-ip`
   - Or add individual A records for each tenant

4. **SSL/TLS**:
   - Use wildcard certificate: `*.bookme.ma`
   - Or individual certificates per tenant

## Troubleshooting Checklist

- [ ] `.env` has `TENANT_BASE_DOMAIN=localhost`
- [ ] Django server restarted after env changes
- [ ] Verified setting with `python manage.py shell -c "from django.conf import settings; print(settings.TENANT_BASE_DOMAIN)"`
- [ ] Checked existing domains: `Domain.objects.all()`
- [ ] Converted old domains if needed: `python manage.py convert_domains_localhost`
- [ ] Browser cache cleared
- [ ] No HSTS cached (check chrome://net-internals/#hsts)

## Related Files

- **Settings**: `src/bookme/settings/base.py`
- **Signals**: `src/tenants_core/tenant/signals.py`
- **Admin**: `src/tenants_core/tenant/admin.py`
- **Management Command**: `src/tenants_core/tenant/management/commands/convert_domains_localhost.py`
