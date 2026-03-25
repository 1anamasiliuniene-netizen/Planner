"""
Django REST Framework ViewSets for Planner API
Provides CRUD operations and filtering for all models.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import (
    Workspace, Membership, Project, Task, Event, Reminder,
    Note, QuickNote
)
from .serializers import (
    UserSerializer, MembershipSerializer, WorkspaceSerializer,
    WorkspaceDetailSerializer, ProjectSerializer, ProjectDetailSerializer,
    TaskSerializer, TaskListSerializer, EventSerializer, ReminderSerializer,
    NoteSerializer, QuickNoteSerializer
)


# ========================
# Workspace ViewSet
# ========================
class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workspaces.

    list: Get all workspaces for the current user
    create: Create a new workspace
    retrieve: Get workspace details
    update: Update workspace
    destroy: Delete workspace

    Custom actions:
    - members: List workspace members
    - share: Share workspace with another user
    """
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type']
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']

    def get_queryset(self):
        """Return workspaces for the current user."""
        return Workspace.objects.filter(
            membership__user=self.request.user
        ).prefetch_related('members').distinct()

    def get_serializer_class(self):
        """Use detailed serializer for retrieve, list uses default."""
        if self.action == 'retrieve':
            return WorkspaceDetailSerializer
        return self.serializer_class

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a workspace."""
        workspace = self.get_object()
        serializer = UserSerializer(workspace.members.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share workspace with another user."""
        workspace = self.get_object()
        username = request.data.get('username')
        role = request.data.get('role', 'member')

        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)
            Membership.objects.get_or_create(
                workspace=workspace,
                user=user,
                defaults={'role': role}
            )
            return Response({
                'status': 'success',
                'message': f'Workspace shared with {username}'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ========================
# Project ViewSet
# ========================
class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for projects.

    list: Get all projects in user's workspaces
    create: Create a new project
    retrieve: Get project details
    update: Update project
    destroy: Delete project

    Custom actions:
    - archive: Archive a project
    - tasks: List project tasks
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workspace', 'is_archived']
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']

    def get_queryset(self):
        """Return projects in user's workspaces."""
        return Project.objects.filter(
            workspace__membership__user=self.request.user
        ).distinct()

    def get_serializer_class(self):
        """Use detailed serializer for retrieve."""
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a project."""
        project = self.get_object()
        project.is_archived = True
        project.archived_at = timezone.now()
        project.save()
        return Response({
            'status': 'success',
            'message': 'Project archived'
        })

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks in the project."""
        project = self.get_object()
        tasks = project.tasks.all()
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


# ========================
# Task ViewSet
# ========================
class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tasks.

    list: Get all tasks in user's workspaces
    create: Create a new task
    retrieve: Get task details
    update: Update task
    destroy: Delete task

    Custom actions:
    - toggle: Toggle task completion status
    - share: Share task with users
    - overdue: Get overdue tasks
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workspace', 'project', 'is_completed', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['due_datetime', 'priority', 'title']
    ordering = ['due_datetime', 'priority']

    def get_queryset(self):
        """Return tasks in user's workspaces."""
        return Task.objects.filter(
            workspace__membership__user=self.request.user
        ).select_related('workspace', 'project').prefetch_related('shared_with').distinct()

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle task completion status."""
        task = self.get_object()
        task.is_completed = not task.is_completed
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share task with other users."""
        task = self.get_object()
        user_ids = request.data.get('user_ids', [])

        from django.contrib.auth.models import User
        users = User.objects.filter(id__in=user_ids)
        task.shared_with.add(*users)

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks."""
        now = timezone.now()
        overdue_tasks = self.get_queryset().filter(
            due_datetime__lt=now,
            is_completed=False
        )
        serializer = TaskListSerializer(overdue_tasks, many=True)
        return Response(serializer.data)


# ========================
# Event ViewSet
# ========================
class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for events.

    list: Get all events in user's workspaces
    create: Create a new event
    retrieve: Get event details
    update: Update event
    destroy: Delete event
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workspace']
    search_fields = ['title', 'location']
    ordering_fields = ['start_time']
    ordering = ['start_time']

    def get_queryset(self):
        """Return events in user's workspaces."""
        return Event.objects.filter(
            workspace__membership__user=self.request.user
        ).select_related('workspace').distinct()


# ========================
# Reminder ViewSet
# ========================
class ReminderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reminders.

    list: Get all reminders
    create: Create a new reminder
    retrieve: Get reminder details
    update: Update reminder
    destroy: Delete reminder

    Custom actions:
    - resolve: Mark reminder as resolved
    - unresolved: Get unresolved reminders
    """
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_resolved']
    ordering_fields = ['due_datetime']
    ordering = ['due_datetime']

    def get_queryset(self):
        """Return reminders for user's tasks and events."""
        from django.db.models import Q
        return Reminder.objects.filter(
            Q(task__workspace__membership__user=self.request.user) |
            Q(event__workspace__membership__user=self.request.user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a reminder as resolved."""
        reminder = self.get_object()
        reminder.is_resolved = True
        reminder.save()
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved reminders."""
        unresolved = self.get_queryset().filter(is_resolved=False)
        serializer = self.get_serializer(unresolved, many=True)
        return Response(serializer.data)


# ========================
# Note ViewSet
# ========================
class NoteViewSet(viewsets.ModelViewSet):
    """API endpoint for notes."""
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return notes for user's tasks."""
        return Note.objects.filter(
            task__workspace__membership__user=self.request.user
        ).distinct()


# ========================
# QuickNote ViewSet
# ========================
class QuickNoteViewSet(viewsets.ModelViewSet):
    """API endpoint for quick notes."""
    serializer_class = QuickNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['display_type', 'shared_workspace']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return quick notes for the current user."""
        return QuickNote.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user to the current request user."""
        serializer.save(user=self.request.user)

