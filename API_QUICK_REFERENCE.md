# API Quick Reference Guide

## Quick Start

### Access API
```
Base URL: http://localhost:8000/api/
Docs:     http://localhost:8000/api/docs/
Schema:   http://localhost:8000/api/schema/
```

### Authentication
```bash
# Login via browser at /api/docs/
# Or use SessionID in requests
```

---

## Most Common Endpoints

### Get Your Workspaces
```bash
curl http://localhost:8000/api/workspaces/
```

### Get Your Tasks (Not Done, Sorted by Due Date)
```bash
curl "http://localhost:8000/api/tasks/?is_completed=false&ordering=due_datetime"
```

### Create New Task
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": 1,
    "title": "New Task",
    "due_datetime": "2026-03-27T17:00:00",
    "priority": 1,
    "is_completed": false
  }'
```

### Toggle Task Complete
```bash
curl -X POST http://localhost:8000/api/tasks/1/toggle/
```

### Get Overdue Tasks
```bash
curl http://localhost:8000/api/tasks/overdue/
```

### Get Unresolved Reminders
```bash
curl http://localhost:8000/api/reminders/unresolved/
```

---

## Filtering Cheat Sheet

| Resource | Common Filters |
|----------|---|
| Tasks | `?is_completed=false` `?priority=1` `?workspace=1` `?ordering=-due_datetime` |
| Projects | `?is_archived=false` `?workspace=1` |
| Events | `?workspace=1` `?ordering=start_time` |
| QuickNotes | `?display_type=list` `?ordering=-updated_at` |
| Reminders | `?is_resolved=false` `?ordering=due_datetime` |

---

## Endpoints by Resource

### Workspaces
```
GET    /api/workspaces/               (list)
POST   /api/workspaces/               (create)
GET    /api/workspaces/{id}/          (detail)
PATCH  /api/workspaces/{id}/          (update)
DELETE /api/workspaces/{id}/          (delete)
GET    /api/workspaces/{id}/members/  (list members)
POST   /api/workspaces/{id}/share/    (share with user)
```

### Projects
```
GET    /api/projects/                 (list)
POST   /api/projects/                 (create)
GET    /api/projects/{id}/            (detail)
PATCH  /api/projects/{id}/            (update)
DELETE /api/projects/{id}/            (delete)
POST   /api/projects/{id}/archive/    (archive)
GET    /api/projects/{id}/tasks/      (list tasks)
```

### Tasks
```
GET    /api/tasks/                    (list)
POST   /api/tasks/                    (create)
GET    /api/tasks/{id}/               (detail)
PATCH  /api/tasks/{id}/               (update)
DELETE /api/tasks/{id}/               (delete)
POST   /api/tasks/{id}/toggle/        (toggle done/not-done)
POST   /api/tasks/{id}/share/         (share with users)
GET    /api/tasks/overdue/            (list overdue)
```

### Events
```
GET    /api/events/                   (list)
POST   /api/events/                   (create)
GET    /api/events/{id}/              (detail)
PATCH  /api/events/{id}/              (update)
DELETE /api/events/{id}/              (delete)
```

### Reminders
```
GET    /api/reminders/                (list)
POST   /api/reminders/                (create)
GET    /api/reminders/{id}/           (detail)
PATCH  /api/reminders/{id}/           (update)
DELETE /api/reminders/{id}/           (delete)
POST   /api/reminders/{id}/resolve/   (mark resolved)
GET    /api/reminders/unresolved/     (list unresolved)
```

### Notes
```
GET    /api/notes/                    (list)
POST   /api/notes/                    (create)
GET    /api/notes/{id}/               (detail)
PATCH  /api/notes/{id}/               (update)
DELETE /api/notes/{id}/               (delete)
```

### QuickNotes
```
GET    /api/quicknotes/               (list)
POST   /api/quicknotes/               (create)
GET    /api/quicknotes/{id}/          (detail)
PATCH  /api/quicknotes/{id}/          (update)
DELETE /api/quicknotes/{id}/          (delete)
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (not logged in) |
| 403 | Forbidden (no permission) |
| 404 | Not Found |
| 500 | Server Error |

---

## Request Headers

```bash
curl -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     http://localhost:8000/api/tasks/
```

---

## Pagination Example

```bash
# Get page 1 (default, 50 items)
curl http://localhost:8000/api/tasks/?page=1

# Response includes:
# {
#   "count": 156,
#   "next": "http://localhost:8000/api/tasks/?page=2",
#   "previous": null,
#   "results": [...]
# }
```

---

## Search Examples

```bash
# Search tasks by title
curl "http://localhost:8000/api/tasks/?search=urgent"

# Search workspaces
curl "http://localhost:8000/api/workspaces/?search=Personal"

# Search events by location
curl "http://localhost:8000/api/events/?search=Conference"
```

---

## Ordering Examples

```bash
# Tasks sorted by priority (ascending)
curl "http://localhost:8000/api/tasks/?ordering=priority"

# Tasks sorted by due date (descending)
curl "http://localhost:8000/api/tasks/?ordering=-due_datetime"

# Events sorted by start time
curl "http://localhost:8000/api/events/?ordering=start_time"
```

---

## Combined Filters Example

```bash
# Get incomplete tasks due today, sorted by priority
curl "http://localhost:8000/api/tasks/?is_completed=false&ordering=priority&search=today"

# Get active projects in workspace 1
curl "http://localhost:8000/api/projects/?workspace=1&is_archived=false&ordering=name"

# Get all unresolved reminders, newest first
curl "http://localhost:8000/api/reminders/?is_resolved=false&ordering=-due_datetime"
```

---

## Testing with Python

```python
import requests

session = requests.Session()
BASE_URL = "http://localhost:8000/api"

# Login first (if not using session authentication)
# session.post(f"{BASE_URL}/auth/login/", data={...})

# Get tasks
response = session.get(f"{BASE_URL}/tasks/")
tasks = response.json()

print(f"Total tasks: {tasks['count']}")
for task in tasks['results']:
    print(f"  - {task['title']} ({task['due_datetime']})")
```

---

## Testing with JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Get tasks
fetch(`${BASE_URL}/tasks/`)
  .then(r => r.json())
  .then(data => {
    console.log(`Total tasks: ${data.count}`);
    data.results.forEach(task => {
      console.log(`  - ${task.title}`);
    });
  });

// Create task
fetch(`${BASE_URL}/tasks/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    workspace: 1,
    title: 'New task',
    due_datetime: '2026-03-27T17:00:00'
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Installed Packages

```
✅ djangorestframework==3.17.1
✅ django-filter==25.2
✅ drf-spectacular==0.29.0
```

## Configuration Files

```
📄 /mysite/settings.py     - Added REST_FRAMEWORK config
📄 /mysite/urls.py         - Added API URLs
📄 /planner/api_urls.py    - API route definitions
📄 /planner/serializers.py - Request/response schemas
📄 /planner/viewsets.py    - API endpoints (56 total)
```

---

**Total Endpoints**: 56  
**Resource Types**: 7 (Workspaces, Projects, Tasks, Events, Reminders, Notes, QuickNotes)  
**HTTP Methods**: GET, POST, PUT, PATCH, DELETE  
**Authentication**: SessionAuthentication (required on all endpoints)  

---

For more details, see `API_ENDPOINTS.md` or visit `/api/docs/` for interactive testing.

