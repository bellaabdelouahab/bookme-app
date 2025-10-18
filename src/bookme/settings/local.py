"""
Local development settings.
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

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
LOGGING["loggers"]["bookme"]["level"] = "DEBUG"

# Disable template caching
for template in TEMPLATES:
    template["OPTIONS"]["debug"] = True

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
