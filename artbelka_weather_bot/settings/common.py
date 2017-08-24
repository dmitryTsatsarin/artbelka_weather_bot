# -*- coding: utf-8 -*-

"""
Django settings for artbelka_weather_bot project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

__author__ = 'forward'

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!yx*l$jxio6(nu)hbx&h2&%_bwr@%kr&st!z@=71r@1f#=neh%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
MEDIA_URL = '/media/'


# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'djcelery',
    'easy_thumbnails',
    'weather_bot_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'artbelka_weather_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'artbelka_weather_bot.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'celery.utils.dispatch.signal': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'tsd_cache_table',
    }
}


# CELERYBEAT_SCHEDULE = {
#     'post_by_schedule': {
#         'task': 'shop_bot_app.tasks.post_by_schedule',
#         'schedule': crontab(minute="*"),
#     },
# }

BOT_REQUEST_TIME_THRESHOLD = 5 # уведомлять о всех запросах дольше 5 секунд
LOGUTILS_REQUEST_TIME_THRESHOLD = BOT_REQUEST_TIME_THRESHOLD

GRAPPELLI_SWITCH_USER = True
GRAPPELLI_ADMIN_TITLE = 'Artbelka Weather Bots'

EMAIL_FULL_ADDRESS = 'bots@mail.artbelka.by'
EMAIL_SHOP_BOT_ADMIN = 'dmitry.tsatsarin@gmail.com'

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (50, 50), 'crop': True},
        '400x400': {'size': (400, 400), 'crop': 'scale'},
        '400x400bad': {'size': (400, 400), 'crop': True, 'quality':10},
    },
}

THUMBNAIL_WIDGET_OPTIONS = {'size': (400, 400), 'crop': 'scale'}

ADMIN_TELEGRAM_DEFAULT_CHAT_ID = 53986880 # мой id по умолчанию