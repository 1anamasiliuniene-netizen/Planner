#!/usr/bin/env bash
# ============================================================================
# PythonAnywhere Deployment Script for Planner App
# ============================================================================
# Run this INSIDE a PythonAnywhere Bash console.
#
# BEFORE running:
# 1. Log in to pythonanywhere.com
# 2. Go to "Web" tab → "Add a new web app"
#    - Choose "Manual configuration" (NOT Django)
#    - Pick Python 3.13 (highest available that supports Django 6.0)
#    - Your app URL will be something like: anamasiliuniene.eu.pythonanywhere.com
#      (since anamasiliuniene.pythonanywhere.com is already in use)
# 3. Open a Bash console from the Dashboard
# 4. Run this script:  bash deploy_pythonanywhere.sh
# ============================================================================

set -e  # Exit on error

# ── CONFIGURATION ───────────────────────────────────────────────────────────
# Change these to match your setup:
PA_USER="anamasiliuniene"                                     # PythonAnywhere username
APP_DOMAIN="${PA_USER}.eu.pythonanywhere.com"                  # Your second web app domain
GITHUB_REPO="https://github.com/anamasiliuniene/Planner.git"
PROJECT_DIR="/home/${PA_USER}/Planner"                         # Where to clone
DJANGO_DIR="${PROJECT_DIR}/mysite"                             # manage.py location
VENV_DIR="/home/${PA_USER}/.virtualenvs/planner-venv"          # Virtualenv path
PYTHON_VERSION="python3.13"                                    # PythonAnywhere Python version
# ────────────────────────────────────────────────────────────────────────────

echo "=== Step 1: Clone repository ==="
if [ -d "$PROJECT_DIR" ]; then
    echo "Directory exists, pulling latest..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    git clone "$GITHUB_REPO" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo "=== Step 2: Create virtualenv ==="
if [ ! -d "$VENV_DIR" ]; then
    mkvirtualenv planner-venv --python=/usr/bin/${PYTHON_VERSION}
else
    echo "Virtualenv exists, activating..."
fi
source "${VENV_DIR}/bin/activate"

echo "=== Step 3: Install dependencies ==="
cd "$PROJECT_DIR"
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Step 4: Create production my_settings.py ==="
cat > "${DJANGO_DIR}/mysite/my_settings.py" << 'SETTINGS_EOF'
import os

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'CHANGE-ME-to-a-real-random-secret-key-in-production!'
)

DEBUG = False

ALLOWED_HOSTS = [
    'anamasiliuniene.eu.pythonanywhere.com',
    # Add your custom domain here if you get one later
]
SETTINGS_EOF
echo "  ✓ my_settings.py created (edit SECRET_KEY!)"

echo "=== Step 5: Run migrations ==="
cd "$DJANGO_DIR"
python manage.py migrate

echo "=== Step 6: Create superuser ==="
echo "  → Creating superuser (skip if already exists)..."
python manage.py createsuperuser --username Ana --email your@email.com --noinput 2>/dev/null || echo "  (superuser may already exist)"

echo "=== Step 7: Collect static files ==="
python manage.py collectstatic --noinput

echo "=== Step 8: Seed demo data ==="
python manage.py create_demo_data
echo "  ✓ Demo data created"

echo ""
echo "============================================"
echo "  CODE IS READY!"
echo "============================================"
echo ""
echo "Now configure in PythonAnywhere Web tab:"
echo ""
echo "1. WSGI file — click the link to edit it, replace ALL content with:"
echo "   (see deploy_pythonanywhere.sh comments below)"
echo ""
echo "2. Static files mappings:"
echo "   URL: /static/    → /home/${PA_USER}/Planner/mysite/staticfiles/"
echo "   URL: /media/     → /home/${PA_USER}/Planner/mysite/media/"
echo ""
echo "3. Virtualenv path:"
echo "   ${VENV_DIR}"
echo ""
echo "4. Source code directory:"
echo "   ${DJANGO_DIR}"
echo ""
echo "5. Click 'Reload' button"
echo ""
echo "============================================"

# ============================================================================
# WSGI FILE CONTENT — Copy this into PythonAnywhere's WSGI config file:
# ============================================================================
#
# import os
# import sys
#
# # Add your project directory to the sys.path
# project_home = '/home/anamasiliuniene/Planner/mysite'
# if project_home not in sys.path:
#     sys.path.insert(0, project_home)
#
# # Add the parent directory too (for imports)
# project_parent = '/home/anamasiliuniene/Planner'
# if project_parent not in sys.path:
#     sys.path.insert(0, project_parent)
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
#
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()
#
# ============================================================================

