"""
API Integration Requirements and Setup Instructions

To enable REST API, install these packages:

1. Django REST Framework:
   pip install djangorestframework

2. Django Filter (for filtering/search):
   pip install django-filter

3. CORS Headers (if serving from different domain):
   pip install django-cors-headers

4. API Documentation (optional but recommended):
   pip install drf-spectacular

After installation, update settings:
"""

# settings.py additions:
# 1. Add to INSTALLED_APPS:
INSTALLED_APPS = [
    # ...existing apps...
    'rest_framework',
    'django_filters',
    'corsheaders',  # optional
]

# 2. Add REST Framework configuration:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# 3. Add to MIDDLEWARE (before CommonMiddleware):
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # optional
    # ...other middleware...
]

# 4. Add CORS settings (optional):
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
]

# 5. Update main urls.py:
"""
from django.urls import path, include
from planner.api_urls import urlpatterns as api_urls

urlpatterns = [
    # ...existing patterns...
    path('', include(api_urls)),
]
"""

# 6. Run migrations (if any):
# python manage.py migrate

# 7. Test API:
# Navigate to http://127.0.0.1:8000/api/ to see all endpoints
# Documentation at http://127.0.0.1:8000/api/docs/

