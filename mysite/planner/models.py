from django.db import models
from django.contrib.auth.models import User

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
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

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
    due_datetime = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, blank=True, related_name="shared_tasks")

    def __str__(self):
        return self.title

class Event(WorkspaceModel):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

class EventSeen(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seen_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_events')
    seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')

class Reminder(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(blank=True)
    due_datetime = models.DateTimeField(blank=True, null=True)  # <-- combined date & time
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message} ({self.due_datetime})"

class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class QuickNote(models.Model):
    DISPLAY_CHOICES = [
        ('plain', 'Plain'),
        ('list', 'Bulleted list'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quicknotes")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='quicknote_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shared_workspace = models.ForeignKey(
        'Workspace',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='shared_notes'
    )
    display_type = models.CharField(max_length=10, choices=DISPLAY_CHOICES, default='plain')

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class QuickNoteSeen(models.Model):
    note = models.ForeignKey(QuickNote, on_delete=models.CASCADE, related_name='seen_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_quicknotes')
    seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('note', 'user')
