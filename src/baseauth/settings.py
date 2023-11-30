"""Django settings for CAS project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/

Before deployment please see
https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/
"""

import os
import re
import sys
from email.utils import getaddresses
from urllib.parse import urlparse

import environ
import ldap
from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

env = environ.Env()
env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = '.'.join(__name__.split('.')[:-1])

try:
    from .secret_key import SECRET_KEY
except ImportError:
    from django.core.management.utils import get_random_secret_key

    with open(os.path.join(BASE_DIR, PROJECT_NAME, 'secret_key.py'), 'w+') as f:
        SECRET_KEY = get_random_secret_key()
        f.write("SECRET_KEY = '%s'\n" % SECRET_KEY)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

# Detect if executed under test
TESTING = any(
    test in sys.argv
    for test in (
        'test',
        'csslint',
        'jenkins',
        'jslint',
        'jtest',
        'lettuce',
        'pep8',
        'pyflakes',
        'pylint',
        'sloccount',
    )
)

DOCKER = env.bool('DOCKER', default=True)

SITE_URL = env.str('SITE_URL')

FORCE_SCRIPT_NAME = env.str('FORCE_SCRIPT_NAME', default='/cas')

SITE_HOSTNAME = urlparse(SITE_URL).hostname

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[SITE_HOSTNAME])

BEHIND_PROXY = env.bool('BEHIND_PROXY', default=True)

DJANGO_ADMINS = env('DJANGO_ADMINS', default=None)

if DJANGO_ADMINS:
    ADMINS = getaddresses([DJANGO_ADMINS])
    MANAGERS = ADMINS

SUPERUSERS = env.tuple('DJANGO_SUPERUSERS', default=())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'mama_cas',
    'axes',
    'captcha',
    'corsheaders',
    # Project apps
    'core',
    'general',
]

# Authentication Backends
AUTH_BACKENDS_TO_USE = env.list('AUTHENTICATION_BACKENDS', default=['django'])

# Axes is always used to prevent brute-force attacks
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
]

# Now all configurable authentication backends are added
for backend in AUTH_BACKENDS_TO_USE:
    # The default django user model backend
    if backend == 'django':
        AUTHENTICATION_BACKENDS.append('django.contrib.auth.backends.ModelBackend')

    if backend == 'cas':
        INSTALLED_APPS.append('django_cas_ng')
        AUTHENTICATION_BACKENDS.append('django_cas_ng.backends.CASBackend')

        CAS_SERVER_URL = env.str('CAS_SERVER', default=f'{SITE_URL}cas/')
        CAS_LOGIN_MSG = None
        CAS_LOGGED_MSG = None
        CAS_RENEW = False
        CAS_LOGOUT_COMPLETELY = True
        CAS_RETRY_LOGIN = True
        CAS_VERSION = env.str('CAS_VERSION', default='3')
        CAS_APPLY_ATTRIBUTES_TO_USER = True
        CAS_REDIRECT_URL = env.str('CAS_REDIRECT_URL', default=FORCE_SCRIPT_NAME or '/')
        CAS_CHECK_NEXT = env.bool('CAS_CHECK_NEXT', default=True)
        CAS_VERIFY_CERTIFICATE = env.bool('CAS_VERIFY_CERTIFICATE', default=True)
        CAS_RENAME_ATTRIBUTES = env.dict('CAS_RENAME_ATTRIBUTES', default={})

    # A generically configurable LDAP authentication backend
    # See https://django-auth-ldap.readthedocs.io/en/latest/authentication.html for details
    if backend == 'ldap':
        AUTH_LDAP_CONNECTION_OPTIONS = {
            ldap.OPT_X_TLS_CACERTFILE: '/etc/ssl/certs/ca-certificates.crt',
            ldap.OPT_X_TLS_NEWCTX: 0,
        }

        AUTH_LDAP_SERVER_URI = env.str('AUTH_LDAP_SERVER_URI')
        AUTH_LDAP_BIND_DN = env.str('AUTH_LDAP_BIND_DN')
        AUTH_LDAP_BIND_PASSWORD = env.str('AUTH_LDAP_BIND_PASSWORD')
        try:
            AUTH_LDAP_USER_DN_TEMPLATE = env.str('AUTH_LDAP_USER_DN_TEMPLATE')
        except environ.ImproperlyConfigured:
            AUTH_LDAP_USER_SEARCH_USER_TEMPLATE = env.str(
                'AUTH_LDAP_USER_SEARCH_USER_TEMPLATE'
            )
            try:
                AUTH_LDAP_USER_SEARCH_BASE = env.str('AUTH_LDAP_USER_SEARCH_BASE')
                AUTH_LDAP_USER_SEARCH = LDAPSearch(
                    AUTH_LDAP_USER_SEARCH_BASE,
                    ldap.SCOPE_SUBTREE,
                    AUTH_LDAP_USER_SEARCH_USER_TEMPLATE,
                )
            except environ.ImproperlyConfigured:
                AUTH_LDAP_USER_SEARCH_BASE_LIST = env.str(
                    'AUTH_LDAP_USER_SEARCH_BASE_LIST'
                ).split(';')
                searches = [
                    LDAPSearch(
                        x.strip(),
                        ldap.SCOPE_SUBTREE,
                        AUTH_LDAP_USER_SEARCH_USER_TEMPLATE,
                    )
                    for x in AUTH_LDAP_USER_SEARCH_BASE_LIST
                ]
                AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(*searches)

        AUTH_LDAP_USER_ATTR_MAP = env.dict(
            'AUTH_LDAP_USER_ATTR_MAP',
            default={'first_name': 'givenName', 'last_name': 'sn', 'email': 'mail'},
        )

        AUTH_LDAP_ALWAYS_UPDATE_USER = True
        AUTH_LDAP_CACHE_TIMEOUT = 0

        AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

# CAS
MAMA_CAS_SERVICES = [
    {
        'SERVICE': fr'^http[s]?://{re.escape(urlparse(SITE_URL).hostname)}',
        'CALLBACKS': ['core.utils.get_attributes'],
        'LOGOUT_ALLOW': True,
        # 'LOGOUT_URL': '',
    }
]

MAMA_CAS_ENABLE_SINGLE_SIGN_OUT = True
"""Email settings."""
SERVER_EMAIL = 'error@%s' % urlparse(SITE_URL).hostname

EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST = env.str('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=25)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_LOCALTIME = env.bool('EMAIL_USE_LOCALTIME', default=True)

EMAIL_SUBJECT_PREFIX = '{} '.format(
    env.str('EMAIL_SUBJECT_PREFIX', default='[CAS]').strip()
)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, '..', 'tmp', 'emails')

    if not os.path.exists(EMAIL_FILE_PATH):
        os.makedirs(EMAIL_FILE_PATH)

""" Https settings """
if SITE_URL.startswith('https'):
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000

X_FRAME_OPTIONS = 'DENY'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]
if 'cas' in AUTH_BACKENDS_TO_USE:
    MIDDLEWARE.append('django_cas_ng.middleware.CASMiddleware')

AXES_LOCKOUT_URL = reverse_lazy('locked_out')
AXES_VERBOSE = DEBUG

if BEHIND_PROXY:
    MIDDLEWARE += ['general.middleware.SetRemoteAddrFromForwardedFor']
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = f'{PROJECT_NAME}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
            'string_if_invalid': "[invalid variable '%s'!]" if DEBUG else '',
        },
    }
]

WSGI_APPLICATION = f'{PROJECT_NAME}.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_DB', default=f'django_{PROJECT_NAME}'),
        'USER': env.str('POSTGRES_USER', default=f'django_{PROJECT_NAME}'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', default=f'password_{PROJECT_NAME}'),
        'HOST': f'{PROJECT_NAME}-postgres' if DOCKER else 'localhost',
        'PORT': env.str('POSTGRES_PORT', default='5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
        )
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Vienna'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (('de', _('German')), ('en', _('English')))

LANGUAGES_DICT = dict(LANGUAGES)

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'locale_mama_cas'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_DIRS = (
    '{}{}'.format(os.path.normpath(os.path.join(BASE_DIR, 'static')), os.sep),
)
STATIC_URL = '{}/s/'.format(FORCE_SCRIPT_NAME if FORCE_SCRIPT_NAME else '')
STATIC_ROOT = '{}{}'.format(
    os.path.normpath(os.path.join(BASE_DIR, 'assets', 'static')), os.sep
)

MEDIA_URL = '{}/m/'.format(FORCE_SCRIPT_NAME if FORCE_SCRIPT_NAME else '')
MEDIA_ROOT = '{}{}'.format(
    os.path.normpath(os.path.join(BASE_DIR, 'assets', 'media')), os.sep
)

FILE_UPLOAD_PERMISSIONS = 0o644

if FORCE_SCRIPT_NAME:
    WHITENOISE_STATIC_PREFIX = '/s/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
"""Logging."""
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d '
                '%(message)s'
            )
        },
        'simple': {'format': '%(levelname)s %(message)s'},
        'simple_with_time': {'format': '%(levelname)s %(asctime)s %(message)s'},
    },
    'handlers': {
        'null': {'level': 'DEBUG', 'class': 'logging.NullHandler'},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'application.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 1000,
            'use_gzip': True,
            'delay': True,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'stream_to_console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
        'rq_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple_with_time',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': True,
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console', 'file', 'mail_admins'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'rq.worker': {
            'handlers': ['rq_console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
"""Cache settings."""
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{}:{}/0'.format(
            f'{PROJECT_NAME}-redis' if DOCKER else 'localhost',
            env.str('REDIS_PORT', default='6379'),
        ),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}
"""Session settings."""
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_NAME = f'sessionid_{PROJECT_NAME}'
SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN', default=None)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_NAME = f'csrftoken_{PROJECT_NAME}'
CSRF_COOKIE_DOMAIN = env.str('CSRF_COOKIE_DOMAIN', default=None)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

CORS_ALLOW_CREDENTIALS = env.bool('CORS_ALLOW_CREDENTIALS', default=False)
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=False)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

HOME_REDIRECT = reverse_lazy('cas_login')

# Axes settings
AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = 1  # number in hours

CAPTCHA_FLITE_PATH = '/usr/bin/flite'

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(
        MIDDLEWARE.index('django.contrib.sessions.middleware.SessionMiddleware'),
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INTERNAL_IPS = ('127.0.0.1',)

    if 'ldap' in AUTH_BACKENDS_TO_USE:
        LOGGING['loggers']['django_auth_ldap'] = {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
