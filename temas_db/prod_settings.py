"""
Django settings for temas_db project.

PRODUCTION SETTINGS --> MAKE SURE to have secret.txt with your Django secret key NOT in VCS.

"""

import os

# SECURITY WARNING: keep the secret key used in production secret!
with open('secret.txt') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
# The Browseable API is only available in Debug mode and will throw errors otherwise.
# Also, Static filles are not served in production mode, serve seperately with NGINX
DEBUG = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # Setup Sentry Logging with for WARNING level
        # Coming from django logging this will include mainly 4XXs as WARNING
        # and 5XX server errors as ERROR
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django': {
            # Use console and sentry for all django base logging from WARNING
            # upwards by default or by querying ENV variable DJANGO_LOG_LEVEL
            'handlers': ['console', 'sentry'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
    },
}

ALLOWED_HOSTS = ['127.0.0.1', '192.168.0.206', '104.248.16.215', 'nco-temas.tk', 'api.nco-temas.tk']

# Application definition

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

CORS_ORIGIN_ALLOW_ALL = True
