"""
Celery configuration for BookMe.
"""
import os

from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookme.settings.local")

app = Celery("bookme")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure logging for Celery."""
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
