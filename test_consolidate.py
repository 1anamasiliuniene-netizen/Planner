#!/usr/bin/env python3
"""
Test-based consolidation that uses Django's test client.
"""
import os
import sys
import json

mysite_path = '/Users/anamasiliuniene/PycharmProjects/PythonProject43/mysite'
sys.path.insert(0, mysite_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

import django
django.setup()

from django.test import Client
from planner.models import Workspace, Task, Project, Event, Membership
from django.contrib.auth.models import User

# Step 1: Check before
print("\n=== BEFORE CONSOLIDATION ===")
workspaces_before = list(Workspace.objects.filter(id__in=[5, 6]).values('id', 'name'))
print(f"Workspaces: {workspaces_before}")

# Step 2: Consolidate
print("\n=== CONSOLIDATING ===")
try:
    family = Workspace.objects.get(pk=5)
    family_shared = Workspace.objects.get(pk=6)

    print(f"Family: {family.projects.count()} projects")
    print(f"Family Shared: {family_shared.projects.count()} projects")

    # Move all content
    for p in family_shared.projects.all():
        p.workspace = family
        p.save()

    Task.objects.filter(workspace=family_shared).update(workspace=family)
    Event.objects.filter(workspace=family_shared).update(workspace=family)

    for m in Membership.objects.filter(workspace=family_shared):
        Membership.objects.get_or_create(workspace=family, user=m.user, defaults={"role": m.role})

    family_shared.delete()
    print("✓ Consolidation complete")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 3: Check after
print("\n=== AFTER CONSOLIDATION ===")
workspaces_after = list(Workspace.objects.filter(id__in=[5, 6]).values('id', 'name'))
print(f"Workspaces: {workspaces_after}")

print("\n✓ Script finished")

