from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Search
    path("search/", views.search, name="search"),

    # Demo
    path("demo/login/", views.demo_login, name="demo_login"),
    path("demo/reset/", views.demo_reset, name="demo_reset"),

    # Dashboard
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),

    # Workspaces
    path("workspaces/create/", views.workspace_create, name="workspace_create"),
    path("workspaces/<int:pk>/", views.workspace_detail, name="workspace_detail"),
    path("workspaces/<int:pk>/edit/", views.workspace_edit, name="workspace_edit"),
    path("workspaces/<int:pk>/delete/", views.workspace_delete, name="workspace_delete"),

    # Projects
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/archive/", views.project_archive, name="project_archive"),
    path("projects/<int:pk>/restore/", views.project_restore, name="project_restore"),
    path("projects/archived/", views.project_archived_list, name="project_archived_list"),
    path("workspaces/<int:workspace_id>/projects/", views.project_list, name="project_list"),

    # Tasks
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/toggle/", views.task_toggle, name="task_toggle"),
    path("tasks/<int:pk>/edit/", views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("tasks/<int:pk>/share/", views.share_task, name="share_task"),
    path('tasks/<int:task_id>/add-reminder/', views.reminder_create_for_task, name='reminder_create_for_task'),
    path("tasks/<int:task_id>/add_note/", views.note_create_for_task, name="note_create_for_task"),
    path('task/<int:pk>/update-due/', views.task_update_due, name='task_update_due'),

    # Notes (legacy alias to memos)
    path("notes/", views.quicknote_list, name="note_list"),

    # Events
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/edit/", views.event_update, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),

    # QuickNotes
    path('memos/', views.quicknote_list, name='quicknote_list'),
    path('memos/create/', views.quicknote_create, name='quicknote_create'),
    path('memos/<int:pk>/', views.quicknote_detail, name='quicknote_detail'),
    path('memos/<int:pk>/edit/', views.quicknote_update, name='quicknote_update'),
    path('memos/<int:pk>/delete/', views.quicknote_delete, name='quicknote_delete'),

    # Reminders
    path("reminders/", views.reminder_list, name="reminder_list"),
    path("reminders/create/", views.reminder_create, name="reminder_create"),
    path("reminders/<int:pk>/edit/", views.reminder_update, name="reminder_update"),
    path("reminders/<int:pk>/delete/", views.reminder_delete, name="reminder_delete"),
    path('reminder/<int:reminder_id>/resolve/', views.reminder_resolve, name='reminder_resolve'),

    # Authentication
    path("accounts/login/", auth_views.LoginView.as_view(template_name="user/login.html"), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/signup/", views.signup, name="signup"),

    # Password Reset Flow
    path(
        "accounts/password_reset/",
        views.PlannerPasswordResetView.as_view(
            template_name="user/password_reset_form.html",
            email_template_name="user/password_reset_email.html",
            subject_template_name="user/password_reset_subject.txt",
            success_url="/accounts/password_reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        views.PlannerPasswordResetDoneView.as_view(template_name="user/password_reset_done.html"),
        name="password_reset_done",
    ),
    path("accounts/reset/<uidb64>/<token>/", views.PlannerPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("r/<uidb64>/<token>/", views.PlannerPasswordResetConfirmView.as_view(), name="password_reset_confirm_short"),
    path(
        "accounts/reset/done/",
        views.PlannerPasswordResetCompleteView.as_view(template_name="user/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
