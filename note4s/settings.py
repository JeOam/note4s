# -*- coding: utf-8 -*-

"""
    settings.py
    ~~~~~~~
"""
import os

JWT_SECRET = '''s40n"o4BRY55y)qG'&A7'@?'_e]XY-3'''

REDIS_HOST = os.environ.get("CDN_ANALYTICS_REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.environ.get("CDN_ANALYTICS_REDIS_PORT", 6379)
REDIS_DB = os.environ.get("CDN_ANALYTICS_REDIS_DB", 1)

PG_URL = os.environ.get("PG_URL", "postgres+psycopg2://note4s_test:note4s_test@127.0.0.1:5432/note4s_test?sslmode=disable")


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s '
                      '%(processName)s %(filename)s - %(funcName)s - %(lineno)d] '
                      '%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'INFO',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': "",
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
