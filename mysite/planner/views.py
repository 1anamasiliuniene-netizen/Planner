from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import (
    TaskForm,
    EventForm,
    ReminderForm,
    ProfileForm,
    CrispyPasswordChangeForm,
    TaskShareForm,
    WorkspaceForm,
    ProjectForm,
)
from .models import Task, Event, Reminder, Workspace, Membership, Project, Note
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date


# -----------------------
# Utilities
# -----------------------
def user_in_workspace(workspace, user):
    """Check if a user belongs to a workspace via Membership."""
    return Membership.objects.filter(workspace=workspace, user=user).exists()


def group_tasks_by_workspace_project(tasks):
    grouped = {}
    for task in tasks:
        workspace = task.workspace
        project = task.project
        grouped.setdefault(workspace, {})
        grouped[workspace].setdefault(project, [])
        grouped[workspace][project].append(task)
    return grouped


# -----------------------
# Profile
# -----------------------
@login_required
def profile_view(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    password_form = CrispyPasswordChangeForm(user=user)

    if request.method == "POST":
        if "profile_submit" in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("profile")
        elif "password_submit" in request.POST:
            password_form = CrispyPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("profile")
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

    return render(request, "user/profile.html", {"profile_form": profile_form, "password_form": password_form})


@login_required
def logout_view(request):
    """Allow logout via direct URL access (GET) and form submit (POST)."""
    logout(request)
    return redirect("login")


# -----------------------
# Token generator
# -----------------------
class EmailPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{timestamp}"


email_token_generator = EmailPasswordResetTokenGenerator()


# -----------------------
# Redirect mixin
# -----------------------
class RedirectAuthenticatedUserMixin:
    """Redirect authenticated users from password reset pages."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(request.GET.get("next", "dashboard"))
        return super().dispatch(request, *args, **kwargs)


# -----------------------
# Password Reset Views
# -----------------------
class PlannerPasswordResetView(RedirectAuthenticatedUserMixin, auth_views.PasswordResetView):
    template_name = "user/password_reset_form.html"
    email_template_name = "user/password_reset_email.html"
    subject_template_name = "user/password_reset_subject.txt"
    token_generator = email_token_generator

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
            "domain_override": self.request.get_host(),
        }
        form.save(**opts)
        from django.views.generic.edit import FormView
        return FormView.form_valid(self, form)


class PlannerPasswordResetDoneView(RedirectAuthenticatedUserMixin, auth_views.PasswordResetDoneView):
    template_name = "user/password_reset_done.html"


class PlannerPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "user/password_reset_confirm.html"
    success_url = "/accounts/reset/done/"
    token_generator = email_token_generator

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.user
        response = super().form_valid(form)
        login(self.request, user)
        messages.success(self.request, "Password updated. You are now logged in.")
        return response


class PlannerPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "user/password_reset_complete.html"


# -----------------------
# Signup
# -----------------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect(request.GET.get("next", "dashboard"))
    else:
        form = UserCreationForm()
    return render(request, "user/signup.html", {"form": form})


# -----------------------
# Dashboard
# -----------------------
@login_required
def dashboard(request):
    # Workspaces visible to current user
    workspaces = Workspace.objects.filter(membership__user=request.user).distinct()

    selected_date = parse_date(request.GET.get("date", "")) or timezone.localdate()
    tasks_due_today = (
        Task.objects.filter(
            workspace__in=workspaces,
            due_datetime__date=selected_date,
            is_completed=False,
        )
        .select_related("workspace", "project")
        .prefetch_related("notes", "reminder_set")
        .order_by("due_datetime")
    )

    return render(request, "planner/dashboard.html", {
        "workspaces": workspaces,
        "tasks_due_today": tasks_due_today,
        "selected_date": selected_date.isoformat(),
    })

# -----------------------
# Project Views
# -----------------------
@login_required
def project_list(request, workspace_id):
    workspace = get_object_or_404(Workspace, pk=workspace_id)
    if not Membership.objects.filter(workspace=workspace, user=request.user).exists():
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    projects = Project.objects.filter(workspace=workspace)
    return render(request, "planner/projects.html", {"workspace": workspace, "projects": projects})


@login_required
def project_detail(request, pk):
    """Nested project page: edit project and manage tasks inside it."""
    project = get_object_or_404(Project, pk=pk)
    workspace = project.workspace

    if not user_in_workspace(workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    tasks = Task.objects.filter(project=project)

    project_form = ProjectForm(request.POST or None, instance=project, user=request.user)
    project_form.fields["workspace"].initial = workspace
    task_form = TaskForm(request.POST or None, user=request.user)

    if request.method == "POST":
        if "project_submit" in request.POST:
            if project_form.is_valid():
                project_form.save()
                messages.success(request, "Project updated successfully.")
                return redirect("project_detail", pk=project.pk)

        elif "task_submit" in request.POST:
            task_form = TaskForm(request.POST, user=request.user)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.workspace = workspace
                task.project = project
                task.save()
                messages.success(request, "Task added to project.")
                return redirect("project_detail", pk=project.pk)

    context = {
        "workspace": workspace,
        "project": project,
        "project_form": project_form,
        "tasks": tasks,
        "task_form": task_form,
        "is_create_mode": False,
    }
    return render(request, "planner/project_detail.html", context)


@login_required
def project_create(request):
    """Create project using project_detail template (no standalone form page)."""
    user_workspaces = Workspace.objects.filter(membership__user=request.user)
    if not user_workspaces.exists():
        messages.info(request, "Create a workspace first to add projects.")
        return redirect("workspace_create")

    if request.method == "POST":
        project_form = ProjectForm(request.POST, user=request.user)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            if not Membership.objects.filter(workspace=project.workspace, user=request.user).exists():
                messages.error(request, "You cannot create a project in a workspace you are not part of.")
                return redirect("dashboard")
            project.save()
            project.members.add(request.user)
            messages.success(request, "Project created successfully.")
            return redirect("project_detail", pk=project.pk)
    else:
        initial_workspace_id = request.GET.get("workspace")
        initial_workspace = user_workspaces.filter(pk=initial_workspace_id).first() if initial_workspace_id else user_workspaces.first()
        project_form = ProjectForm(user=request.user, initial={"workspace": initial_workspace})

    workspace = project_form.initial.get("workspace") if hasattr(project_form, "initial") else None
    if not workspace:
        workspace = user_workspaces.first()

    return render(
        request,
        "planner/project_detail.html",
        {
            "workspace": workspace,
            "project": None,
            "project_form": project_form,
            "tasks": [],
            "task_form": None,
            "is_create_mode": True,
            "workspace_projects": Project.objects.filter(workspace=workspace) if workspace else Project.objects.none(),
        },
    )

# -----------------------
# Workspace Views
# -----------------------
@login_required
def workspace_detail(request, pk):
    """Nested workspace page: edit workspace, manage projects & tasks."""
    workspace = get_object_or_404(Workspace, pk=pk)

    if not user_in_workspace(workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    projects = Project.objects.filter(workspace=workspace)
    tasks = Task.objects.filter(workspace=workspace)

    workspace_form = WorkspaceForm(request.POST or None, request.FILES or None, instance=workspace)
    project_form = ProjectForm(request.POST or None, user=request.user)
    project_form.fields["workspace"].initial = workspace
    task_form = TaskForm(request.POST or None, user=request.user)

    if request.method == "POST":
        if "workspace_submit" in request.POST:
            if workspace_form.is_valid():
                workspace_form.save()
                messages.success(request, "Workspace updated successfully.")
                return redirect("workspace_detail", pk=workspace.pk)

        elif "project_submit" in request.POST:
            project_form = ProjectForm(request.POST, user=request.user)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.workspace = workspace
                project.save()
                project.members.add(request.user)
                messages.success(request, "Project added.")
                return redirect("workspace_detail", pk=workspace.pk)

        elif "task_submit" in request.POST:
            task_form = TaskForm(request.POST, user=request.user)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.workspace = workspace
                task.save()
                messages.success(request, "Task added.")
                return redirect("workspace_detail", pk=workspace.pk)

    context = {
        "workspace": workspace,
        "workspace_form": workspace_form,
        "projects": projects,
        "project_form": project_form,
        "tasks": tasks,
        "task_form": task_form,
        "is_create_mode": False,
    }
    return render(request, "planner/workspace_detail.html", context)


@login_required
def workspace_create(request):
    """Create workspace using workspace_detail template (no standalone form page)."""
    if request.method == "POST":
        workspace_form = WorkspaceForm(request.POST, request.FILES)
        if workspace_form.is_valid():
            workspace = workspace_form.save()
            Membership.objects.get_or_create(workspace=workspace, user=request.user)
            messages.success(request, "Workspace created successfully.")
            return redirect("workspace_detail", pk=workspace.pk)
    else:
        workspace_form = WorkspaceForm()

    return render(
        request,
        "planner/workspace_detail.html",
        {
            "workspace": None,
            "workspace_form": workspace_form,
            "projects": [],
            "project_form": None,
            "tasks": [],
            "task_form": None,
            "is_create_mode": True,
            "workspaces": Workspace.objects.filter(membership__user=request.user),
        },
    )


@login_required
def workspace_edit(request, pk):
    """Legacy route: keep URL compatibility and redirect to workspace detail."""
    return redirect("workspace_detail", pk=pk)


@login_required
def workspace_delete(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)
    if not user_in_workspace(workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    if request.method == "POST":
        workspace.delete()
        messages.success(request, "Workspace deleted successfully.")
    return redirect("dashboard")

# -----------------------
# Task Views
# -----------------------
@login_required
def task_list(request):
    tasks = Task.objects.filter(workspace__membership__user=request.user).select_related("workspace", "project").order_by(
        "workspace__name", "project__name", "due_datetime", "title"
    )
    grouped_tasks = group_tasks_by_workspace_project(tasks)
    return render(request, "planner/tasks.html", {"grouped_tasks": grouped_tasks})


@login_required
def task_detail(request, pk):
    """Task page used for editing an existing task."""
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    workspace = task.workspace

    if not user_in_workspace(workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    sibling_tasks = Task.objects.filter(project=project).exclude(pk=task.pk) if project else []
    task_form = TaskForm(request.POST or None, instance=task, user=request.user)

    if request.method == "POST" and "task_submit" in request.POST:
        if task_form.is_valid():
            updated = task_form.save(commit=False)
            if not user_in_workspace(updated.workspace, request.user):
                messages.error(request, "Invalid workspace.")
                return redirect("task_list")
            updated.save()
            messages.success(request, "Task updated successfully.")
            return redirect("task_detail", pk=task.pk)

    context = {
        "workspace": workspace,
        "project": project,
        "task": task,
        "sibling_tasks": sibling_tasks,
        "task_form": task_form,
        "is_create_mode": False,
    }
    return render(request, "planner/task_detail.html", context)


@login_required
def task_create(request):
    """Create task using task_detail template (no standalone task_form page)."""
    form = TaskForm(request.POST or None, user=request.user)

    if request.method == "POST" and "task_submit" in request.POST:
        if form.is_valid():
            task = form.save(commit=False)
            if not user_in_workspace(task.workspace, request.user):
                messages.error(request, "Invalid workspace.")
                return redirect("task_list")
            task.save()
            messages.success(request, "Task created.")
            return redirect("task_detail", pk=task.pk)

    if not form.fields["workspace"].queryset.exists():
        messages.info(request, "Create a workspace first to add tasks.")
        return redirect("workspace_create")
    if not form.fields["project"].queryset.exists():
        messages.info(request, "Create a project first to add tasks.")
        return redirect("project_create")

    return render(
        request,
        "planner/task_detail.html",
        {
            "workspace": None,
            "project": None,
            "task": None,
            "sibling_tasks": [],
            "task_form": form,
            "is_create_mode": True,
        },
    )


@login_required
def task_update(request, pk):
    """Legacy edit route kept for compatibility; use task_detail UI."""
    return redirect("task_detail", pk=pk)


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST" and user_in_workspace(task.workspace, request.user):
        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed"])

    # Prefer returning to where the action was triggered (dashboard/project/task list).
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)

    if task.project_id:
        return redirect("project_detail", pk=task.project_id)
    return redirect("task_list")


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if user_in_workspace(task.workspace, request.user):
        if request.method == "POST":
            task.delete()
            messages.success(request, "Task deleted.")
            return redirect("project_detail", pk=task.project.pk)
    return render(request, "planner/task_confirm_delete.html", {"task": task})


@login_required
def share_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not user_in_workspace(task.workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("task_list")
    if request.method == "POST":
        form = TaskShareForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task shared successfully.")
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskShareForm(instance=task)
    return render(request, "planner/task_share.html", {"form": form, "task": task})

def reminder_create_for_task(request, task_id):
    """Create a reminder for a specific task from the quick-add form."""
    task = get_object_or_404(Task, pk=task_id)

    if not user_in_workspace(task.workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("task_list")

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        due_datetime_str = request.POST.get("due_datetime", "").strip()

        if message:
            reminder = Reminder.objects.create(
                task=task,
                message=message,
                due_datetime=due_datetime_str if due_datetime_str else None,
            )
            messages.success(request, "Reminder added.")
        else:
            messages.warning(request, "Please enter a reminder message.")

    # Redirect back to the referring page (task detail or project detail)
    return redirect(request.META.get('HTTP_REFERER', f'/tasks/{task_id}/'))

def note_create_for_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title or content:
            Note.objects.create(task=task, title=title, content=content)
    return redirect('project_detail', pk=task.project.pk)



# -----------------------
# Event Views
# -----------------------
@login_required
def event_list(request):
    events = Event.objects.filter(workspace__membership__user=request.user)
    return render(request, "planner/events.html", {"events": events})


@login_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            workspace = form.cleaned_data.get("workspace")
            if not user_in_workspace(workspace, request.user):
                messages.error(request, "Invalid workspace.")
                return redirect("event_list")
            event = form.save(commit=False)
            event.workspace = workspace
            event.save()
            messages.success(request, "Event created.")
            return redirect("event_list")
    else:
        form = EventForm()
    return render(request, "planner/event_form.html", {"form": form})


@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not user_in_workspace(event.workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("event_list")
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated.")
            return redirect("event_list")
    else:
        form = EventForm(instance=event)
    return render(request, "planner/event_form.html", {"form": form})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if user_in_workspace(event.workspace, request.user):
        if request.method == "POST":
            event.delete()
            messages.success(request, "Event deleted.")
            return redirect("event_list")
    return render(request, "planner/event_confirm_delete.html", {"event": event})


# -----------------------
# Reminder Views
# -----------------------
@login_required
def reminder_list(request):
    reminders = Reminder.objects.filter(workspace__membership__user=request.user)
    return render(request, "planner/reminders.html", {"reminders": reminders})


@login_required
def reminder_create(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            workspace = form.cleaned_data.get("workspace")
            if not user_in_workspace(workspace, request.user):
                messages.error(request, "Invalid workspace.")
                return redirect("reminder_list")
            reminder = form.save(commit=False)
            reminder.workspace = workspace
            reminder.save()
            messages.success(request, "Reminder created.")
            return redirect("reminder_list")
    else:
        form = ReminderForm()
    return render(request, "planner/reminder_form.html", {"form": form})


@login_required
def reminder_update(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk)
    if not user_in_workspace(reminder.workspace, request.user):
        messages.error(request, "Access denied.")
        return redirect("reminder_list")
    if request.method == "POST":
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, "Reminder updated.")
            return redirect("reminder_list")
    else:
        form = ReminderForm(instance=reminder)
    return render(request, "planner/reminder_form.html", {"form": form})


@login_required
def reminder_delete(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk)
    if user_in_workspace(reminder.workspace, request.user):
        if request.method == "POST":
            reminder.delete()
            messages.success(request, "Reminder deleted.")
            return redirect("reminder_list")
    return render(request, "planner/reminder_confirm_delete.html", {"reminder": reminder})

def reminder_resolve(request, reminder_id):
    reminder = get_object_or_404(Reminder, pk=reminder_id)
    reminder.is_resolved = True
    reminder.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def note_list(request):
    """Minimal placeholder for notes."""
    notes = []
    return render(request, "planner/notes.html", {"notes": notes})
