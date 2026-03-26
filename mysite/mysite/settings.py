import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-me-before-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# CSRF trusted origins (required by Django 4.0+ for production POST forms)
CSRF_TRUSTED_ORIGINS = [
    f'https://{host}' for host in ALLOWED_HOSTS if not host.startswith('localhost') and not host.startswith('127.')
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Application definition

INSTALLED_APPS = [
    'planner',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'drf_spectacular',
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]
CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'planner.middleware.DemoReadOnlyMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'planner.context_processors.navbar_reminders',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Vilnius'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@planner.local'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


PASSWORD_RESET_TIMEOUT = 3600  # 1 hour


# ========================
# Django REST Framework Settings
# ========================
REST_FRAMEWORK = {
    # Default authentication for API
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Default permission classes
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    # Filtering and searching
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Schema generation (drf-spectacular)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Default renderer classes
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # Datetime format
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S',
    # Exception handler
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# ========================
# drf-spectacular Configuration
# ========================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Planner REST API',
    'DESCRIPTION': 'Complete REST API for Task Planner application with workspaces, projects, tasks, events, reminders, and notes.',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_INCLUDE_SCHEMA': True,
    'SCHEMA_PATH_PREFIX': '/api',
    'SCHEMA_MOUNT_PATH': '/api/schema/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorizationData': True,
        'displayOperationId': True,
    },
    'SERVERS': [
        {
            'url': 'http://localhost:8001' if DEBUG else 'https://{}'.format(ALLOWED_HOSTS[0] if ALLOWED_HOSTS else 'localhost'),
            'description': 'Development server' if DEBUG else 'Production server',
        },
    ],
    'TAGS': [
        {
            'name': 'Workspaces',
            'description': 'Workspace management endpoints',
        },
        {
            'name': 'Projects',
            'description': 'Project management endpoints',
        },
        {
            'name': 'Tasks',
            'description': 'Task management endpoints',
        },
        {
            'name': 'Events',
            'description': 'Event management endpoints',
        },
        {
            'name': 'Reminders',
            'description': 'Reminder management endpoints',
        },
        {
            'name': 'Notes',
            'description': 'Note management endpoints',
        },
        {
            'name': 'QuickNotes',
            'description': 'Quick note management endpoints',
        },
    ],
    'POSTPROCESSING_HOOKS': [],
}
