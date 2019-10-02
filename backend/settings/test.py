from .main import *

DEBUG = True
SCOUT_MONITOR = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
}