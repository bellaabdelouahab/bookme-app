"""
Utilities for host validation against known tenant domains.
"""
from __future__ import annotations

from time import time

from django.conf import settings

try:
    from bookme.tenant.models import Domain
except Exception:  # During early migrations, the model may not be ready
    Domain = None  # type: ignore


_CACHE_TTL = 30  # seconds
_cache = {"ts": 0.0, "hosts": set()}


def _load_hosts_from_db() -> set[str]:
    if Domain is None:
        return set()
    try:
        return set(Domain.objects.values_list("domain", flat=True))
    except Exception:
        # DB not ready or table missing during migrate
        return set()


def get_allowed_hosts_dynamic() -> set[str]:
    """Return dynamic hostnames allowed based on Domain table, cached briefly."""
    now = time()
    if now - _cache["ts"] > _CACHE_TTL:
        _cache["hosts"] = _load_hosts_from_db()
        _cache["ts"] = now
    return set(_cache["hosts"]) | set(settings.ALLOWED_HOSTS)


def host_matches_base_wildcard(host: str) -> bool:
    base = getattr(settings, "TENANT_BASE_DOMAIN", None)
    if not base:
        return False
    return host == base or host.endswith("." + base)
