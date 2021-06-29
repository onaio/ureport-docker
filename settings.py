# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


# import our default settings
from ureport.settings_common import *
import os
import dj_database_url

IS_PROD=True
DEBUG = False
THUMBNAIL_DEBUG = DEBUG
COMPRESS_ENABLED = True


EMPTY_SUBDOMAIN_HOST = 'http://{}'.format(os.environ.get('UREPORT_DOMAIN'))
HOSTNAME = os.environ.get('UREPORT_DOMAIN')
ALLOWED_HOSTS = ['*']

SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_AGE = 10800

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_SECONDS = 86400
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'HTTPS')
SECURE_REDIRECT_EXEMPT =  []
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = False

# these guys will get email from sentry
ADMINS = (
    ('Ona Ops', 'techops+{}@ona.io'.format(os.environ.get('UREPORT_DOMAIN'))),
)

# set the mail settings, we send through gmail
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '587')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '${gmail_user}')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '${gmail_user}')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '${gmail_password}')
EMAIL_USE_TLS = True

MANAGERS = ADMINS

# add gunicorn
INSTALLED_APPS = INSTALLED_APPS + ('gunicorn', 'storages')


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'MISSING_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'MISSING_AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AwS_STORAGE_BUCKET_NAME', 'dl-ureport')
AWS_S3_SECURE_URLS = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# these two settings will cause our aws files to never expire
# see http://developer.yahoo.com/performance/rules.html#expires
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',

}

# static dir is different for prod
STATIC_URL = os.environ.get('STATIC_URL', '/sitestatic/')
COMPRESS_URL = os.environ.get('COMPRESS_URL', '/sitestatic/')

# our media is all on S3
MEDIA_URL = os.environ.get('MEDIA_URL', 'https://dl-ureport.s3.amazonaws.com/')

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

SITE_API_HOST = os.environ.get('SITE_API_HOST', 'https://api.rapidpro.io')


DATABASES['default'] = dj_database_url.config()

# reuse our connections for up to 60 seconds
DATABASES['default']['CONN_MAX_AGE'] = 60

# no debug toolbar in prod
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'smartmin.middleware.AjaxRedirect',
    'django.middleware.locale.LocaleMiddleware',
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'dash.orgs.middleware.SetOrgMiddleware',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

# use our cache backend for sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# trust connections that are coming in on this protocol
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'HTTPS')

# compress arguments
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = [
    dict(STATIC_URL=STATIC_URL, base_template='frame.html', org=None, debug=False, testing=False),
    dict(STATIC_URL=STATIC_URL, base_template='public_base.html', org=None, debug=False, testing=False)
]
COMPRESS_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis-internal.ureport.in')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = os.environ.get('REDIS_DB', '1')

BROKER_URL = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': BROKER_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_RESULT_BACKEND = BROKER_URL
