"""
Django REST Framework Serializers for Planner API
Provides serialization for all models with proper validation.
"""
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Workspace, Membership, Project, Task, Event, Reminder,
    Note, QuickNote, QuickNoteSeen, EventSeen
)


# ========================
# User Serializer
# ========================
class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id']


# ========================
# Membership Serializer
# ========================
class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Workspace membership."""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'workspace', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


# ========================
# Workspace Serializer
# ========================
class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Workspace model with nested members."""
    members = UserSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'type', 'image', 'members', 'member_count']
        read_only_fields = ['id']

    def get_member_count(self, obj):
        return obj.members.count()


# ========================
# Project Serializer
# ========================
class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    task_count = serializers.SerializerMethodField()
    member_names = serializers.StringRelatedField(many=True, source='members', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'workspace', 'name', 'members',
            'member_names', 'is_archived', 'archived_at',
            'task_count'
        ]
        read_only_fields = ['id', 'archived_at']

    def get_task_count(self, obj):
        return obj.tasks.count()


# ========================
# Task Serializer
# ========================
class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with full details."""
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    shared_with_names = serializers.StringRelatedField(many=True, source='shared_with', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'workspace', 'workspace_name', 'project', 'project_name',
            'title', 'description', 'due_datetime', 'priority',
            'is_completed', 'shared_with', 'shared_with_names',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_due_datetime(self, value):
        """Validate that due_datetime is not in the past."""
        if value and value < serializers.DateTimeField().to_representation(value):
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value


class TaskListSerializer(TaskSerializer):
    """Simplified serializer for task list views."""

    class Meta:
        model = Task
        fields = ['id', 'title', 'workspace_name', 'project_name', 'due_datetime', 'is_completed', 'priority']
        read_only_fields = ['id']


# ========================
# Event Serializer
# ========================
class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'workspace', 'workspace_name', 'title',
            'start_time', 'end_time', 'location', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        """Validate that end_time is after start_time."""
        if data.get('end_time') and data.get('start_time'):
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("End time must be after start time.")
        return data


# ========================
# Reminder Serializer
# ========================
class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for Reminder model."""
    task_title = serializers.CharField(source='task.title', read_only=True, allow_null=True)
    event_title = serializers.CharField(source='event.title', read_only=True, allow_null=True)

    class Meta:
        model = Reminder
        fields = [
            'id', 'task', 'task_title', 'event', 'event_title',
            'message', 'due_datetime', 'is_resolved'
        ]
        read_only_fields = ['id']


# ========================
# Note Serializer
# ========================
class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model."""
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'task', 'task_title', 'title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


# ========================
# QuickNote Serializer
# ========================
class QuickNoteSerializer(serializers.ModelSerializer):
    """Serializer for QuickNote model."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    workspace_name = serializers.CharField(source='shared_workspace.name', read_only=True, allow_null=True)

    class Meta:
        model = QuickNote
        fields = [
            'id', 'user', 'user_username', 'title', 'content', 'image',
            'display_type', 'shared_workspace', 'workspace_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


# ========================
# Nested Serializers (for detail views)
# ========================
class WorkspaceDetailSerializer(WorkspaceSerializer):
    """Extended workspace serializer with tasks and projects."""
    projects = ProjectSerializer(many=True, read_only=True)
    tasks = TaskListSerializer(many=True, read_only=True, source='task_set')

    class Meta(WorkspaceSerializer.Meta):
        fields = WorkspaceSerializer.Meta.fields + ['projects', 'tasks']


class ProjectDetailSerializer(ProjectSerializer):
    """Extended project serializer with tasks."""
    tasks = TaskListSerializer(many=True, read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['tasks', 'workspace_name']

