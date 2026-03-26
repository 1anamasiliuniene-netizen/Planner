# Deploy Planner to PythonAnywhere — Step by Step

You already have **anamasiliuniene.pythonanywhere.com** for another app.  
This planner will go on your **second web app** slot.

---

## Step 1 — Create a New Web App

1. Log in to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to **Web** tab → **Add a new web app**
3. Domain: pick **anamasiliuniene.eu.pythonanywhere.com**
   *(this is the free second subdomain PythonAnywhere gives you)*
4. Select **Manual configuration** (NOT "Django")
5. Python version: **3.13** *(highest available that supports Django 6.0)*
6. Click **Next** to create it

---

## Step 2 — Clone the Repo (Bash Console)

Open a **Bash console** from the Dashboard and run:

```bash
cd ~
git clone https://github.com/anamasiliuniene/Planner.git
```

---

## Step 3 — Create Virtualenv

```bash
mkvirtualenv planner-venv --python=/usr/bin/python3.13
```

This activates automatically. If you need to reactivate later:
```bash
workon planner-venv
```

---

## Step 4 — Install Dependencies

```bash
cd ~/Planner
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 5 — Create Production Settings

```bash
nano ~/Planner/mysite/mysite/my_settings.py
```

Paste this (change the SECRET_KEY to something random):

```python
SECRET_KEY = 'put-a-long-random-string-here-at-least-50-chars!'

DEBUG = False

ALLOWED_HOSTS = ['anamasiliuniene.eu.pythonanywhere.com']
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

> **Tip:** Generate a random key:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## Step 6 — Run Migrations & Create Superuser

```bash
cd ~/Planner/mysite
python manage.py migrate
python manage.py createsuperuser
```

Enter your username (`Ana`), email, and password when prompted.

---

## Step 7 — Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Step 8 — Seed Demo Data

```bash
python manage.py create_demo_data
```

---

## Step 9 — Configure WSGI File

Go to **Web** tab → click the **WSGI configuration file** link
(it's something like `/var/www/anamasiliuniene_eu_pythonanywhere_com_wsgi.py`)

**Delete ALL existing content** and paste:

```python
import os
import sys

project_home = '/home/anamasiliuniene/Planner/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

project_parent = '/home/anamasiliuniene/Planner'
if project_parent not in sys.path:
    sys.path.insert(0, project_parent)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Save the file.

---

## Step 10 — Configure Static & Media File Mappings

In the **Web** tab, scroll to **Static files** section and add:

| URL | Directory |
|---|---|
| `/static/` | `/home/anamasiliuniene/Planner/mysite/staticfiles/` |
| `/media/` | `/home/anamasiliuniene/Planner/mysite/media/` |

---

## Step 11 — Set Virtualenv Path

In the **Web** tab → **Virtualenv** section, enter:

```
/home/anamasiliuniene/.virtualenvs/planner-venv
```

---

## Step 12 — Set Source Code Directory

```
/home/anamasiliuniene/Planner/mysite
```

---

## Step 13 — Reload & Test

1. Click the green **Reload** button
2. Visit: **https://anamasiliuniene.eu.pythonanywhere.com**
3. Log in as your superuser or try demo mode

---

## Updating Later

When you make changes locally:

```bash
# Local (Mac):
cd ~/PycharmProjects/PythonProject43
git add -A && git commit -m "your message" && git push origin main

# PythonAnywhere Bash console:
cd ~/Planner
git pull origin main
cd mysite
python manage.py migrate          # only if models changed
python manage.py collectstatic --noinput  # only if static files changed
# Then click Reload in Web tab
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| 500 error | Check **Web** tab → **Error log** (link at bottom) |
| Static/CSS not loading | Verify static files paths in Web tab match exactly |
| Images not showing | Verify `/media/` mapping points to `.../mysite/media/` |
| CSRF errors on forms | Check `CSRF_TRUSTED_ORIGINS` includes your domain in settings |
| "DisallowedHost" | Add your exact domain to `ALLOWED_HOSTS` in `my_settings.py` |

