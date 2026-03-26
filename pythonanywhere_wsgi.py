# ============================================================================
# PythonAnywhere WSGI Configuration File
# ============================================================================
# Copy this ENTIRE content into PythonAnywhere's WSGI config file.
# (Web tab → click the WSGI config file link)
# Replace ALL existing content with this.
# ============================================================================

import os
import sys

# Add your project directory to the sys.path
project_home = '/home/anamasiliuniene/Planner/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add the parent directory too (for imports like requirements)
project_parent = '/home/anamasiliuniene/Planner'
if project_parent not in sys.path:
    sys.path.insert(0, project_parent)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

