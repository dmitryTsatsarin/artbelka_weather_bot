# -*- coding: utf-8 -*-
__author__ = 'forward'

from .common import *
import os
import raven


RAVEN_CONFIG = {
    'dsn': 'https://0a8358c017c24e77b58040c22374f909:6c1ce67f1ea244f6ab9f2a0c428c58e9@sentry.io/241228',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(message)s'
        },
    },
    'handlers': {
        'sentry_self_test_handler': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
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
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['sentry_self_test_handler'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'celery': {
            'level': 'INFO',
            'handlers': ['sentry','console'],
            'propagate': False,
        },
        'weather_bot_app': {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        }
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'weather_bot',
        'USER': 'webrunner',
        'PASSWORD': 'ZHkv8GD4Zab2g4HHNqPn',
        'HOST': 'localhost',
        'PORT': 5432,
        'TEST': {
            'NAME': 'weather_bot_test',
        },
    },
    'stat': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.stat.sqlite3'),
    }
}

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'amqp://rabbitusername:6cae046bd8de29@localhost:5672//artbelka_weather_bot'

ALLOWED_HOSTS = ['*']


WEBSITE_HOST = 'weather.artbelka.by'
WEBHOOK_HOST = WEBSITE_HOST
WEBHOOK_LISTEN = WEBHOOK_HOST
WEBHOOK_PORT = 443

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBSITE_BASE_URL = 'https://%s' % WEBSITE_HOST

#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/mails'

BOT_REQUEST_TIME_THRESHOLD = 20
LOGUTILS_REQUEST_TIME_THRESHOLD = BOT_REQUEST_TIME_THRESHOLD # уведомлять о всех запросах дольше 10 секунд

# выставить токет для botan
#BOTAN_TOKEN =

