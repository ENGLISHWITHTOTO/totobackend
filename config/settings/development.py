import os
from .base import *

DEBUG = True

# Development specific settings
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database for development - using SQLite for simplicity
# DATABASES configuration is inherited from base.py

# Development email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Logging for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
