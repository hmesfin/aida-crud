"""
AIDA-CRUD: Advanced Intelligent Django API CRUD Framework
A comprehensive framework for building DRY, feature-rich CRUD operations
"""

__version__ = "1.0.0"

# Only import if Django is configured
try:
    from django.conf import settings
    settings.INSTALLED_APPS
    
    from .core import *
    from .mixins import *
    from .serializers import *
    from .viewsets import *
    from .filters import *
    from .exporters import *
    from .audit import *
except Exception:
    # Django not configured yet - imports will work once Django project is set up
    pass
