#!/usr/bin/env python3
"""
Direct consolidation and reseed - writes status to file
"""
import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
sys.path.insert(0, '/Users/anamasiliuniene/PycharmProjects/PythonProject43/mysite')

django.setup()

from planner.models import Workspace, Task, Project, Event, Membership
from django.contrib.auth.models import User

status_file = '/tmp/consolidate_status.txt'

def log(msg):
    with open(status_file, 'a') as f:
        f.write(msg + '\n')

# Clear file
open(status_file, 'w').write('=== CONSOLIDATION & RESEED ===\n')

try:
    log("\n1. CONSOLIDATING REAL ACCOUNT")
    family = Workspace.objects.get(pk=5, name="Family")
    family_shared = Workspace.objects.get(pk=6, name="Family Shared")

    log(f"   Found: {family.name}, {family_shared.name}")

    # Move content
    for p in family_shared.projects.all():
        p.workspace = family
        p.save()
    Task.objects.filter(workspace=family_shared).update(workspace=family)
    Event.objects.filter(workspace=family_shared).update(workspace=family)

    for m in Membership.objects.filter(workspace=family_shared):
        Membership.objects.get_or_create(workspace=family, user=m.user, defaults={"role": m.role})

    family_shared.delete()
    log("   ✓ Family Shared deleted, content moved to Family")

except Workspace.DoesNotExist as e:
    log(f"   ! {e} (may already be consolidated)")
except Exception as e:
    log(f"   ✗ ERROR: {e}")

log("\n2. RESEEDING DEMO")
try:
    # Delete old demo workspaces
    demo = User.objects.get(username='demo')
    Workspace.objects.filter(membership__user=demo).delete()
    log("   Deleted old demo workspaces")

    # Run seeding
    from django.core.management import call_command
    call_command('create_demo_data')
    log("   ✓ Demo data reseeded")

except Exception as e:
    log(f"   ✗ ERROR: {e}")

log("\n3. VERIFICATION")
try:
    ana = User.objects.get(username='Ana')
    demo = User.objects.get(username='demo')

    ana_ws = list(Workspace.objects.filter(membership__user=ana).values_list('name').distinct())
    demo_ws = list(Workspace.objects.filter(membership__user=demo).values_list('name').distinct())

    log(f"   Ana workspaces: {[w[0] for w in ana_ws]}")
    log(f"   Demo workspaces: {[w[0] for w in demo_ws]}")

    # Check for Family Shared
    if any('Shared' in w[0] for w in demo_ws):
        log("   ✗ FAILED: Family Shared still present in demo")
    else:
        log("   ✓ SUCCESS: No shared duplicates in demo")

except Exception as e:
    log(f"   ✗ ERROR: {e}")

log("\n=== DONE ===")
print(f"Status written to {status_file}")

