"""
Test settings.
"""
from .base import *  # noqa

DEBUG = True

# Use fast password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use in-memory database for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "test_bookme",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
        "TEST": {
            "NAME": "test_bookme",
        },
    }
}

# Use simpler cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery - run tasks synchronously in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable throttling
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # type: ignore

# Simplified logging
LOGGING = {  # type: ignore
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# MIGRATION_MODULES = DisableMigrations()
