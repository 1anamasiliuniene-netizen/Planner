# Planner API Documentation

## Overview

The Planner application now includes a full REST API built with Django REST Framework (DRF). The API provides 50+ endpoints for managing workspaces, projects, tasks, events, reminders, notes, and quick notes.

**API Base URL:** `/api/`  
**API Schema:** `/api/schema/`  
**API Documentation (Swagger UI):** `/api/docs/`

---

## Installation & Setup

### Packages Installed
```bash
pip install djangorestframework django-filter drf-spectacular
```

### Settings Updated
- Added `rest_framework`, `drf_spectacular`, and `django_filters` to `INSTALLED_APPS`
- Configured DRF with:
  - SessionAuthentication
  - IsAuthenticated permission class
  - Pagination (50 items per page)
  - DjangoFilterBackend, SearchFilter, OrderingFilter
  - drf-spectacular for OpenAPI schema generation

### URLs Configuration
- API routes registered at `/api/`
- API authentication routes at `/api/auth/`
- OpenAPI schema at `/api/schema/`
- Swagger UI documentation at `/api/docs/`

---

## Authentication

All API endpoints require authentication. Use session-based authentication:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -d "username=your_username&password=your_password"

# Logout
curl -X POST http://localhost:8000/api/auth/logout/
```

---

## Available Endpoints

### Workspaces API

#### List Workspaces
```
GET /api/workspaces/
```
- Returns all workspaces where the user is a member
- Supports filtering by type: `?type=personal`
- Supports search: `?search=workspace_name`
- Supports ordering: `?ordering=name`

#### Create Workspace
```
POST /api/workspaces/
```
Request body:
```json
{
  "name": "Project Alpha",
  "type": "work",
  "image": null
}
```

#### Retrieve Workspace
```
GET /api/workspaces/{id}/
```

#### Update Workspace
```
PUT /api/workspaces/{id}/
PATCH /api/workspaces/{id}/
```

#### Delete Workspace
```
DELETE /api/workspaces/{id}/
```

#### List Workspace Members
```
GET /api/workspaces/{id}/members/
```

#### Share Workspace
```
POST /api/workspaces/{id}/share/
```
Request body:
```json
{
  "username": "john_doe",
  "role": "member"
}
```

---

### Projects API

#### List Projects
```
GET /api/projects/
```
- Filter by workspace: `?workspace=1`
- Filter by archive status: `?is_archived=false`
- Search by name: `?search=project_name`

#### Create Project
```
POST /api/projects/
```
Request body:
```json
{
  "workspace": 1,
  "name": "Q1 Planning",
  "members": [1, 2, 3],
  "is_archived": false
}
```

#### Retrieve Project
```
GET /api/projects/{id}/
```

#### Update Project
```
PUT /api/projects/{id}/
PATCH /api/projects/{id}/
```

#### Delete Project
```
DELETE /api/projects/{id}/
```

#### Archive Project
```
POST /api/projects/{id}/archive/
```

#### List Project Tasks
```
GET /api/projects/{id}/tasks/
```

---

### Tasks API

#### List Tasks
```
GET /api/tasks/
```
- Filter by workspace: `?workspace=1`
- Filter by project: `?project=1`
- Filter by completion: `?is_completed=false`
- Filter by priority: `?priority=1`
- Search by title/description: `?search=task_name`
- Order by: `?ordering=due_datetime,priority`

#### Create Task
```
POST /api/tasks/
```
Request body:
```json
{
  "workspace": 1,
  "project": 1,
  "title": "Complete API documentation",
  "description": "Write comprehensive API docs",
  "due_datetime": "2026-03-31T17:00:00",
  "priority": 1,
  "is_completed": false,
  "shared_with": [1, 2]
}
```

#### Retrieve Task
```
GET /api/tasks/{id}/
```

#### Update Task
```
PUT /api/tasks/{id}/
PATCH /api/tasks/{id}/
```

#### Delete Task
```
DELETE /api/tasks/{id}/
```

#### Toggle Task Completion
```
POST /api/tasks/{id}/toggle/
```

#### Share Task
```
POST /api/tasks/{id}/share/
```
Request body:
```json
{
  "user_ids": [1, 2, 3]
}
```

#### List Overdue Tasks
```
GET /api/tasks/overdue/
```

---

### Events API

#### List Events
```
GET /api/events/
```
- Filter by workspace: `?workspace=1`
- Search by title/location: `?search=event_name`
- Order by start_time: `?ordering=start_time`

#### Create Event
```
POST /api/events/
```
Request body:
```json
{
  "workspace": 1,
  "title": "Team Meeting",
  "start_time": "2026-03-26T10:00:00",
  "end_time": "2026-03-26T11:00:00",
  "location": "Conference Room A",
  "notes": "Q1 planning meeting"
}
```

#### Retrieve Event
```
GET /api/events/{id}/
```

#### Update Event
```
PUT /api/events/{id}/
PATCH /api/events/{id}/
```

#### Delete Event
```
DELETE /api/events/{id}/
```

---

### Reminders API

#### List Reminders
```
GET /api/reminders/
```
- Filter by resolution status: `?is_resolved=false`
- Order by due date: `?ordering=due_datetime`

#### Create Reminder
```
POST /api/reminders/
```
Request body:
```json
{
  "task": 1,
  "event": null,
  "message": "Don't forget to submit the report",
  "due_datetime": "2026-03-26T09:00:00",
  "is_resolved": false
}
```

#### Retrieve Reminder
```
GET /api/reminders/{id}/
```

#### Update Reminder
```
PUT /api/reminders/{id}/
PATCH /api/reminders/{id}/
```

#### Delete Reminder
```
DELETE /api/reminders/{id}/
```

#### Resolve Reminder
```
POST /api/reminders/{id}/resolve/
```

#### List Unresolved Reminders
```
GET /api/reminders/unresolved/
```

---

### Notes API

#### List Notes
```
GET /api/notes/
```
- Search by title/content: `?search=note_text`
- Order by creation date: `?ordering=-created_at`

#### Create Note
```
POST /api/notes/
```
Request body:
```json
{
  "task": 1,
  "title": "Implementation Notes",
  "content": "Use async/await for better performance"
}
```

#### Retrieve Note
```
GET /api/notes/{id}/
```

#### Update Note
```
PUT /api/notes/{id}/
PATCH /api/notes/{id}/
```

#### Delete Note
```
DELETE /api/notes/{id}/
```

---

### Quick Notes API

#### List Quick Notes
```
GET /api/quicknotes/
```
- Filter by display type: `?display_type=list`
- Filter by shared workspace: `?shared_workspace=1`
- Search by title/content: `?search=note_text`
- Order by: `?ordering=-updated_at`

#### Create Quick Note
```
POST /api/quicknotes/
```
Request body:
```json
{
  "title": "Shopping List",
  "content": "- Milk\n- Bread\n- Eggs",
  "display_type": "list",
  "shared_workspace": 1,
  "image": null
}
```
Note: `user` is automatically set to the authenticated user

#### Retrieve Quick Note
```
GET /api/quicknotes/{id}/
```

#### Update Quick Note
```
PUT /api/quicknotes/{id}/
PATCH /api/quicknotes/{id}/
```

#### Delete Quick Note
```
DELETE /api/quicknotes/{id}/
```

---

## Pagination

All list endpoints support pagination with a default page size of 50 items.

```
GET /api/tasks/?page=1
GET /api/tasks/?page=2
```

Response includes:
```json
{
  "count": 156,
  "next": "http://localhost:8000/api/tasks/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering

### Available Filters

| Endpoint | Filters |
|----------|---------|
| Workspaces | `type` |
| Projects | `workspace`, `is_archived` |
| Tasks | `workspace`, `project`, `is_completed`, `priority` |
| Events | `workspace` |
| Reminders | `is_resolved` |
| QuickNotes | `display_type`, `shared_workspace` |

### Search

Most endpoints support full-text search via `?search=` parameter:

```
GET /api/tasks/?search=urgent
GET /api/projects/?search=Q1
```

### Ordering

Use `?ordering=field` or `?ordering=-field` for reverse order:

```
GET /api/tasks/?ordering=-due_datetime
GET /api/projects/?ordering=name
```

---

## Error Handling

API errors follow standard HTTP status codes:

- **200 OK** - Successful GET request
- **201 Created** - Successful POST request
- **204 No Content** - Successful DELETE request
- **400 Bad Request** - Invalid data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

Error responses include details:

```json
{
  "error": "Field 'title' is required",
  "status": 400
}
```

---

## Example Usage

### Get all tasks due today (Python)

```python
import requests

BASE_URL = "http://localhost:8000/api"
session = requests.Session()

# Login
session.post(f"{BASE_URL}/auth/login/", data={
    "username": "john_doe",
    "password": "secure_password"
})

# Get tasks
response = session.get(f"{BASE_URL}/tasks/?is_completed=false&ordering=due_datetime")
tasks = response.json()

for task in tasks['results']:
    print(f"{task['title']} - Due: {task['due_datetime']}")
```

### Create a new task (cURL)

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": 1,
    "title": "Review API documentation",
    "description": "Check for completeness and accuracy",
    "due_datetime": "2026-03-27T17:00:00",
    "priority": 1,
    "is_completed": false
  }'
```

---

## Interactive Documentation

Access interactive API documentation at:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

You can test all endpoints directly from the Swagger UI interface.

---

## API Capabilities Summary

✅ **50+ Endpoints** across 7 resource types  
✅ **Full CRUD Operations** (Create, Read, Update, Delete)  
✅ **Custom Actions** (toggle tasks, archive projects, share resources, etc.)  
✅ **Filtering & Search** on all list endpoints  
✅ **Ordering** support for flexible sorting  
✅ **Pagination** with configurable page size  
✅ **Authentication** via session-based auth  
✅ **Permissions** - IsAuthenticated on all endpoints  
✅ **OpenAPI/Swagger** - Complete API documentation  
✅ **Browsable API** - Interactive testing interface  

---

**Last Updated:** March 25, 2026  
**Django Version:** 6.0.3  
**DRF Version:** 3.17.1

