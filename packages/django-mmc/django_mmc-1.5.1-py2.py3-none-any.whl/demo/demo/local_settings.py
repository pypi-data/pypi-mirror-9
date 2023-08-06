# -*- encoding: utf-8 -*-

#MMC_LOCK_TYPE = 'RedisLock'

from settings import INSTALLED_APPS

'''
INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

RAVEN_CONFIG = {
    'dsn': 'https://1c66b94401184cba8c2c3370b5cc6971:11a19e5e6f1c417a928952eee4434fa9@app.getsentry.com/26104',
}
'''
import sys
import django

#print sys.version
#print '>>', django.get_version()

if 'test' not in sys.argv:
    MMC_SUBJECT = '[MMC] Error: %(host)s: %(script)s'
    if django.VERSION[:2] < (1, 7):
        INSTALLED_APPS += ('south',)
