"""
Django settings for temas_db project.

PRODUCTION SETTINGS --> MAKE SURE to have secret.txt with your Django secret key NOT in VCS.

"""

import os
import raven

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
with open('secret.txt') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
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

RAVEN_CONFIG = {
    'dsn': 'https://5db556b9fd9e4116b9910a99bbe031df:d4bd7b5bae5747da90084fd434dca2bc@sentry.io/1273162',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.abspath(BASE_DIR)),
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
