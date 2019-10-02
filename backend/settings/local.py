from .main import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bivver_local',
        'USER': 'root',
        'PASSWORD': 'citrus',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}

CACHES = {
   'default': {
       'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
     }
}
