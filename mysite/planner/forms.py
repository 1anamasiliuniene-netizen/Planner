from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Task, Event, Reminder, Workspace, Project, Note
from django.contrib.auth.forms import PasswordChangeForm

# -----------------------
# Task Form
# -----------------------
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "workspace",
            "project",
            "title",
            "description",
            "due_datetime",
            "priority",
            "is_completed",
        ]
        widgets = {
            "due_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["workspace"].queryset = Workspace.objects.filter(members=user)
        else:
            self.fields["workspace"].queryset = Workspace.objects.none()

        self.fields["project"].queryset = Project.objects.none()

        selected_workspace_id = None
        if self.is_bound:
            selected_workspace_id = self.data.get("workspace")
        elif self.instance and self.instance.pk:
            selected_workspace_id = self.instance.workspace_id

        if selected_workspace_id:
            self.fields["project"].queryset = Project.objects.filter(
                workspace_id=selected_workspace_id,
                workspace__members=user,
            )
        elif user:
            self.fields["project"].queryset = Project.objects.filter(workspace__members=user)

    def clean(self):
        cleaned_data = super().clean()
        workspace = cleaned_data.get("workspace")
        project = cleaned_data.get("project")

        if project and workspace and project.workspace_id != workspace.id:
            self.add_error("project", "Project must belong to selected workspace.")

        return cleaned_data


class TaskShareForm(forms.ModelForm):
    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
        help_text="Select users to share this task with"
    )

    class Meta:
        model = Task
        fields = ["shared_with"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("share", "Share Task", css_class="btn btn-primary"))
# -----------------------
# Event Form
# -----------------------
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["workspace", "title", "start_time", "end_time", "location", "notes"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

# -----------------------
# Note Form
# -----------------------
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Note title", "class": "form-control form-control-sm mb-2"}),
            "content": forms.Textarea(attrs={"placeholder": "Note content", "class": "form-control form-control-sm mb-2", "rows": 2}),
        }

# -----------------------
# Reminder Form
# -----------------------
class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["task", "message", "due_datetime", "is_resolved"]
        widgets = {
            "due_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M"  # important!
            ),
            "message": forms.TextInput(attrs={"placeholder": "Reminder message"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure the datetime value is in the correct format for the input
        if self.instance and self.instance.due_datetime:
            self.initial["due_datetime"] = self.instance.due_datetime.strftime("%Y-%m-%dT%H:%M")

# -----------------------
# Profile Form (Crispy + Bootstrap 5)
# -----------------------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form"
        self.helper.label_class = "form-label"
        self.helper.field_class = "form-control"


# -----------------------
# Password Change Form (Crispy + Bootstrap 5)
# -----------------------
class CrispyPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm styled with Crispy Forms + Bootstrap 5"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form"
        self.helper.label_class = "form-label"
        self.helper.field_class = "form-control"


# -----------------------
# Workspace Form
# -----------------------
class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ["name", "type", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Workspace name"}),
        }


# -----------------------
# Project Form
# -----------------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["workspace", "name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Project name"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["workspace"].queryset = Workspace.objects.filter(members=user)
        else:
            self.fields["workspace"].queryset = Workspace.objects.none()
