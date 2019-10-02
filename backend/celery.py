from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
import scout_apm.celery
from scout_apm.api import Config
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')
app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

Config.set(
    key=settings.SCOUT_KEY,
    name=settings.SCOUT_NAME,
    monitor=settings.SCOUT_MONITOR
)

scout_apm.celery.install()
app.autodiscover_tasks()