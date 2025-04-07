"""
Django settings for the project.
Settings are organized into modular files for better organization.
"""
import os
# Load settings in order of increasing specificity
# This allows settings in later files to override earlier ones
DJANGO_SETTINGS_MODULE = "settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# 1. First, environment
from settings.env import *  # Required first to detect environment

# 2. Core settings modules
from settings.logging import *
from settings.base import *
from settings.database import *

# 3. Third-party integrations
from settings.third_party import *

# 3. Scheduler settings (if needed)
try:
    from settings.scheduler.celery import *
except ImportError:
    pass  # Celery not required

# 4. Environment-specific settings
# Production settings
if PRODUCTION:
    from settings.production import *

# Local development settings (override everything)
if LOCAL:
    try:
        from settings.local import *
    except ImportError:
        pass  # Local settings are optional
