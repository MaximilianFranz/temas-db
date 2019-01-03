"""
Django settings for temas_db project.

DEVELOPMENT SETTINGS
"""

import os


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w)+y2ft^o5xrj@a25=!!xp773ks-#0*k9f3%_30)=ldu_^tb62'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message} in line {lineno} of {funcName} in {filename}',
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
            # 'handlers': ['console'],
            'handlers': ['console',],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
    },
}

ALLOWED_HOSTS = ['127.0.0.1', '192.168.0.206', '104.248.16.215', 'nco-temas.tk', 'api.nco-temas.tk']

# Application definition
CORS_ORIGIN_ALLOW_ALL = True



