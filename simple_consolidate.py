#!/usr/bin/env python3
"""
Direct consolidation script that writes step-by-step to a log file.
"""
import os
import sys

# Setup paths first
mysite_path = '/Users/anamasiliuniene/PycharmProjects/PythonProject43/mysite'
sys.path.insert(0, mysite_path)

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

# Write checkpoint
open('/tmp/check1.txt', 'w').write('Checkpoint 1\n')

# Setup Django
import django
django.setup()

# Write checkpoint
open('/tmp/check2.txt', 'w').write('Checkpoint 2\n')

# Import models
from planner.models import Workspace, Task, Project, Event, Membership
from django.contrib.auth.models import User

# Write checkpoint
open('/tmp/check3.txt', 'w').write('Checkpoint 3\n')

# Get workspaces
try:
    family = Workspace.objects.get(pk=5)
    family_shared = Workspace.objects.get(pk=6)
    open('/tmp/check4.txt', 'w').write(f'Found workspaces: {family.name}, {family_shared.name}\n')

    # Consolidate
    proj_count_before = family_shared.projects.count()
    task_count_before = Task.objects.filter(workspace=family_shared).count()

    # Move projects
    for p in family_shared.projects.all():
        p.workspace = family
        p.save()

    # Move tasks and events
    Task.objects.filter(workspace=family_shared).update(workspace=family)
    Event.objects.filter(workspace=family_shared).update(workspace=family)

    # Migrate members
    for m in Membership.objects.filter(workspace=family_shared):
        Membership.objects.get_or_create(workspace=family, user=m.user, defaults={"role": m.role})

    # Delete
    family_shared.delete()

    # Write success
    open('/tmp/check5.txt', 'w').write(f'SUCCESS: Moved {proj_count_before} projects and {task_count_before} tasks\n')

except Exception as e:
    import traceback
    open('/tmp/check_error.txt', 'w').write(f'ERROR: {e}\n{traceback.format_exc()}\n')

print("Consolidation complete - check /tmp/check*.txt files")

