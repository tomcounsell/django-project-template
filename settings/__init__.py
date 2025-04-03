"""
Django settings for the project.
Settings are organized into modular files for better organization.
"""

# Load settings in order of increasing specificity
# This allows settings in later files to override earlier ones

# 2. Core settings modules
from settings.base import *
from settings.database import *

# 1. First, environment & base configuration
from settings.env import *  # Required first to detect environment
from settings.logging import *
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
