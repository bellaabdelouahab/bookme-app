"""
Local development settings.
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Development tenant domain configuration
# Use .localhost for development instead of .bookme.ma
TENANT_DOMAIN_SUFFIX = ".localhost"

# Development-specific apps
INSTALLED_APPS += [
    "django_extensions",
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

# More verbose logging
LOGGING["loggers"]["tenants_core"]["level"] = "DEBUG"
LOGGING["loggers"]["base_start"]["level"] = "DEBUG"

# Disable template caching
for template in TEMPLATES:
    template["OPTIONS"]["debug"] = True

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable HTTPS redirects in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = None
