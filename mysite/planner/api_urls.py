"""
Django REST Framework URLs for Planner API
Registers all viewsets and provides API documentation.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

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

    # API Documentation
    path('api/docs/', include_docs_urls(
        title='Planner API',
        description='REST API for Task Planner application',
        version='1.0.0'
    )),
]

