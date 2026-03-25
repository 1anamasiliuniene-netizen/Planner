#!/usr/bin/env python
"""
Consolidate Family Shared into Family for the real owner (Ana)
and simplify demo seeding to not create duplicates.
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
sys.path.insert(0, "/Users/anamasiliuniene/PycharmProjects/PythonProject43/mysite")

django.setup()

from planner.models import Workspace, Task, Project, Event, Membership
from django.contrib.auth.models import User

print("=== Consolidating Real Workspaces ===\n")

# Get the real workspaces
try:
    family = Workspace.objects.get(id=5, name="Family")
    family_shared = Workspace.objects.get(id=6, name="Family Shared")
except Workspace.DoesNotExist as e:
    print(f"ERROR: Workspace not found: {e}")
    sys.exit(1)

print("BEFORE:")
print(f"  Family: {family.projects.count()} projects, {Task.objects.filter(workspace=family).count()} tasks, {family.members.count()} members")
print(f"  Family Shared: {family_shared.projects.count()} projects, {Task.objects.filter(workspace=family_shared).count()} tasks, {family_shared.members.count()} members")

# Move all content from Family Shared to Family
for proj in family_shared.projects.all():
    proj.workspace = family
    proj.save()
    print(f"  ✓ Moved project: {proj.name}")

for task in Task.objects.filter(workspace=family_shared):
    task.workspace = family
    task.save()

for event in Event.objects.filter(workspace=family_shared):
    event.workspace = family
    event.save()

# Migrate members from Family Shared to Family
shared_members = list(Membership.objects.filter(workspace=family_shared))
for membership in shared_members:
    Membership.objects.get_or_create(
        workspace=family,
        user=membership.user,
        defaults={"role": membership.role}
    )
    print(f"  ✓ Added member: {membership.user.username} (role: {membership.role})")

# Delete Family Shared
family_shared.delete()

print("\nAFTER:")
print(f"  Family: {family.projects.count()} projects, {Task.objects.filter(workspace=family).count()} tasks, {family.members.count()} members")
print(f"  ✓ Family Shared DELETED\n")

print("=== Real Workspaces Consolidated Successfully ===")

