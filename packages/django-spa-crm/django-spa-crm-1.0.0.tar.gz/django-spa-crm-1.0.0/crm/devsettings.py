from .settings import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "crm",
        "USER": "crm",
        "PASSWORD": "5!7p+%-w%dp5",
        "HOST": "localhost",
        "TEST_MIRROR": "default",
    },
}

LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
    },
    "loggers": {
        "crm": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    }
}

TEST = {
    "USER": "testrunner",
    "PASSWORD": "NoPa$$123",
}

TEST_USERNAME = "testrunner"
TEST_PASSWORD = "NoPa$$123"

del MIDDLEWARE_CLASSES[0]
