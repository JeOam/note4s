# -*- coding: utf-8 -*-

"""
    settings.py
    ~~~~~~~
"""
import os

JWT_SECRET = '''s40n"o4BRY55y)qG'&A7'@?'_e]XY-3'''

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_DB = os.environ.get("REDIS_DB", 1)

GITHUB_ID = os.environ.get("GITHUB_ID", "6bc8273bcb63a84de3ba")
GITHUB_SECRET = os.environ.get("GITHUB_ID", "426b6e5feecf23c58187b99cc285438259285ba2")
MAILGUN_KEY = os.environ.get("MAILGUN_KEY", "key-7b67fe0ce64c61fc44792de3d43fa0ac")

PG_URL = os.environ.get("PG_URL", "postgres+psycopg2://note4s:note4s@127.0.0.1:5432/note4s?sslmode=disable")
GIT_DIR = os.environ.get("GIT_DIR", "GIT_DIR/")

FILE_FOLDER = './Upload/'
ONE_TOKEN_VALID_ONLY = False
DEBUG = os.environ.get("DEBUG", True)
PORT = os.environ.get("PORT", 8888)


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
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
