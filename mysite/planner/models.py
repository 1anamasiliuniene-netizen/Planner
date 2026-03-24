from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# models.py
class Workspace(models.Model):
    WORKSPACE_TYPES = [
        ("personal", "Personal"),
        ("work", "Work"),
        ("family", "Family"),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    image = models.ImageField(upload_to="workspace_images/", blank=True, null=True)
    members = models.ManyToManyField(
        User,
        through="Membership",
        related_name="workspaces"
    )

    def __str__(self):
        return self.name

# Membership: who has access and role
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="member")  # optional: admin/member/etc.
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "workspace")

    def __str__(self):
        return f"{self.user.username} in {self.workspace.name} ({self.role})"


# Base model for all workspace-bound items
class WorkspaceModel(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Project(models.Model):
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="projects")
    members = models.ManyToManyField(User, related_name="projects")

    def __str__(self):
        return f"{self.workspace.name} / {self.name}"


class Task(WorkspaceModel):
    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, blank=True, related_name="shared_tasks")

class Event(WorkspaceModel):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

class Reminder(WorkspaceModel):
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.CASCADE)
    remind_at = models.DateTimeField()
    is_resolved = models.BooleanField(default=False)

