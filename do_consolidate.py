#!/usr/bin/env python3
import os
import sys
import sqlite3

# Write output to file immediately
log_file = '/tmp/consolidate.log'
def log_msg(msg):
    with open(log_file, 'a') as f:
        f.write(msg + '\n')
    sys.stderr.write(msg + '\n')

# Clear previous log
with open(log_file, 'w') as f:
    f.write('=== Consolidation Started ===\n')

log_msg("Step 1: Checking database state")

# First, check the current state
db_path = "/Users/anamasiliuniene/PycharmProjects/PythonProject43/mysite/db.sqlite3"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check if workspaces 5 and 6 exist
cur.execute("SELECT id, name FROM planner_workspace WHERE id IN (5, 6) ORDER BY id")
result_before = cur.fetchall()
log_msg(f"Before: {result_before}")

# Now do the consolidation via Django
log_msg("Step 2: Setting up Django")
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
sys.path.insert(0, '/Users/anamasiliuniene/PycharmProjects/PythonProject43/mysite')

import django
django.setup()
log_msg("Step 3: Django setup complete")

from planner.models import Workspace, Task, Project, Event, Membership

try:
    log_msg("Step 4: Getting workspaces")
    family = Workspace.objects.get(pk=5)
    family_shared = Workspace.objects.get(pk=6)
    log_msg(f"  Found: Family (id={family.id}), Family Shared (id={family_shared.id})")

    # Move projects
    log_msg("Step 5: Moving projects")
    for p in family_shared.projects.all():
        p.workspace = family
        p.save()
        log_msg(f"  → Moved project: {p.name}")

    # Move tasks
    log_msg("Step 6: Moving tasks")
    Task.objects.filter(workspace=family_shared).update(workspace=family)

    # Move events
    log_msg("Step 7: Moving events")
    Event.objects.filter(workspace=family_shared).update(workspace=family)

    # Migrate members
    log_msg("Step 8: Migrating members")
    for m in Membership.objects.filter(workspace=family_shared):
        Membership.objects.get_or_create(workspace=family, user=m.user, defaults={"role": m.role})
        log_msg(f"  → Added member: {m.user.username}")

    # Delete
    log_msg("Step 9: Deleting Family Shared workspace")
    family_shared.delete()

    success = True
    log_msg("Step 10: SUCCESS!")
except Exception as e:
    import traceback
    success = False
    error_msg = str(e)
    log_msg(f"ERROR: {error_msg}")
    log_msg(traceback.format_exc())

# Check after
conn2 = sqlite3.connect(db_path)
cur2 = conn2.cursor()
cur2.execute("SELECT id, name FROM planner_workspace WHERE id IN (5, 6) ORDER BY id")
result_after = cur2.fetchall()

conn.close()
conn2.close()

# Write summary
with open('/tmp/consolidate_result.txt', 'w') as f:
    f.write("BEFORE:\n")
    f.write(str(result_before) + "\n\n")
    f.write("AFTER:\n")
    f.write(str(result_after) + "\n\n")
    if success:
        f.write("✓ SUCCESS: Family Shared consolidated into Family\n")
    else:
        f.write(f"✗ ERROR: {error_msg}\n")

print("Done - check /tmp/consolidate_result.txt")

