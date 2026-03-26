================================================================================
                        PLANNER - TASK MANAGEMENT SYSTEM
================================================================================

PROJECT OVERVIEW
================================================================================
Planner is a REST API-based task and workspace management application
built with Django and Django REST Framework (DRF). It provides a complete
API for managing workspaces, projects, tasks, reminders, events, notes,
and supporting multi-user collaboration.

The application is a backend API service providing 50+ endpoints with
OpenAPI 3.0 documentation, Swagger UI, and ReDoc.

Tech Stack:
- Backend: Django 6.0.3, Python 3.14.2
- Database: SQLite3
- API: Django REST Framework with drf_spectacular
- Documentation: OpenAPI 3.0 / Swagger UI & ReDoc
- Authentication: Session-based with DRF

================================================================================
KEY FEATURES
================================================================================

1. WORKSPACES
   - Create personal, work, or family workspaces
   - Add custom images to workspaces
   - Invite users and assign roles (admin/member)
   - View workspace membership
   - Share workspaces with other users

2. PROJECTS
   - Organize tasks within projects
   - Archive completed projects
   - View project members
   - Restore archived projects

3. TASKS
   - Create tasks with titles and descriptions
   - Set due dates and priorities
   - Mark tasks as complete/incomplete
   - Share tasks with other users
   - Attach notes to tasks
   - View overdue tasks
   - Filter by status, priority, workspace

4. EVENTS
   - Create calendar events with start/end times
   - Add location and notes to events
   - Track event visibility (EventSeen)
   - View events by workspace
   - Sort and filter events

5. REMINDERS
   - Set reminders for tasks and events
   - Combine date and time for precise reminders
   - Mark reminders as resolved
   - View unresolved reminders
   - Sort reminders by due date

6. QUICK NOTES (Memos)
   - Create quick notes with optional images
   - Support for plain text or bulleted list display
   - Share notes with specific workspaces
   - Auto-timestamping (created_at, updated_at)
   - Track note visibility (QuickNoteSeen)

7. AUTHENTICATION & AUTHORIZATION
   - User registration and login
   - Password reset functionality
   - Role-based access control (member/admin)
   - Demo account with read-only access
   - Session-based authentication
   - API token support via REST framework

8. SEARCH FUNCTIONALITY
   - Global search across projects, tasks, and more
   - Filter by workspace and status

9. CALENDAR VIEW
   - Visual calendar interface
   - Event scheduling and management

10. DASHBOARD
    - Central hub showing workspaces, tasks, and events
    - Quick access to all features
    - Real-time reminders in navbar