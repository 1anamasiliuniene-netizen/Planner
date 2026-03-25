"""
Django REST Framework URLs for Planner API
Registers all viewsets and provides API documentation.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .viewsets import (
    WorkspaceViewSet, ProjectViewSet, TaskViewSet,
    EventViewSet, ReminderViewSet, NoteViewSet, QuickNoteViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'events', EventViewSet, basename='event')
router.register(r'reminders', ReminderViewSet, basename='reminder')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'quicknotes', QuickNoteViewSet, basename='quicknote')

# API URLs
urlpatterns = [
    # REST API routes
    path('api/', include(router.urls)),

    # API Authentication
    path('api/auth/', include('rest_framework.urls')),

    # API Schema and Documentation (using drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

