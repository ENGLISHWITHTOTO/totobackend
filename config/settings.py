"""
Django settings for config project.

This file imports the appropriate settings based on the environment.
"""

import os
from .settings.base import *

# Determine which settings to use based on environment
ENVIRONMENT = os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.development")

if "production" in ENVIRONMENT:
    from .settings.production import *
elif "development" in ENVIRONMENT:
    from .settings.development import *
