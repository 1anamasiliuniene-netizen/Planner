"""
Management command: create_demo_data
Mirrors the real owner's workspaces (names, types, images) into the demo
account so the showcase looks identical to the live app.
Run:  python manage.py create_demo_data
Re-run any time to reset the demo to a clean state.
"""
import shutil
import os
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demopassword123"
OWNER_USERNAME = "Ana"          # <-- change if your username is different


class Command(BaseCommand):
    help = "Create or reset demo user and showcase data"

    def handle(self, *args, **options):
        from planner.models import (
            Workspace, Membership, Project, Task,
            Event, Reminder, QuickNote,
        )

        # ── Demo user ────────────────────────────────────────────────────────
        demo_user, created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={"first_name": "Demo", "email": "demo@example.com"},
        )
        demo_user.set_password(DEMO_PASSWORD)
        demo_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created demo user"))
        else:
            self.stdout.write("Demo user exists — resetting data")
            Workspace.objects.filter(membership__user=demo_user).delete()

        # ── Find the real owner ───────────────────────────────────────────────
        owner = User.objects.filter(username=OWNER_USERNAME).first()
        if not owner:
            # Fallback: pick the first non-demo staff/superuser
            owner = (
                User.objects.filter(is_superuser=True)
                .exclude(username=DEMO_USERNAME)
                .first()
            )

        # ── Copy owner workspaces → demo workspaces ───────────────────────────
        now = timezone.now()
        demo_workspaces = []

        owner_workspaces = (
            Workspace.objects.filter(membership__user=owner)
            .order_by("pk")
            if owner
            else Workspace.objects.none()
        )

        # Filter: skip "shared" workspaces to avoid duplicates
        # (consolidate via real account instead)
        owner_workspaces = [
            ws for ws in owner_workspaces
            if "shared" not in ws.name.lower()
        ]

        for real_ws in owner_workspaces:
            new_image_path = ""
            if real_ws.image:
                # Copy the image file so the demo workspace has its own copy.
                # Use slugified workspace name as filename to keep each workspace unique.
                src = os.path.join(settings.MEDIA_ROOT, str(real_ws.image))
                if os.path.exists(src):
                    ext = os.path.splitext(src)[1]
                    slug = real_ws.name.lower().replace(" ", "_")
                    dest_name = f"workspace_images/demo_{slug}{ext}"
                    dest = os.path.join(settings.MEDIA_ROOT, dest_name)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(src, dest)
                    new_image_path = dest_name

            demo_ws = Workspace.objects.create(
                name=real_ws.name,
                type=real_ws.type,
                image=new_image_path,
            )
            Membership.objects.create(workspace=demo_ws, user=demo_user, role="admin")
            demo_workspaces.append(demo_ws)
            self.stdout.write(f"  Workspace: {demo_ws.name} ({demo_ws.type})")

        # Fallback if owner had no workspaces
        if not demo_workspaces:
            for name, ws_type in [("Personal", "personal"), ("Work", "work"), ("Family", "family")]:
                ws = Workspace.objects.create(name=name, type=ws_type)
                Membership.objects.create(workspace=ws, user=demo_user, role="admin")
                demo_workspaces.append(ws)

        # ── Assign projects/tasks/events/notes round-robin across workspaces ──
        # Use the first 3 distinct workspaces for the demo content
        ws_count = len(demo_workspaces)
        def ws(i):
            return demo_workspaces[i % ws_count]

        projects_spec = [
            (ws(0), "Health & Fitness", [
                ("Morning jog — 5 km",           True,  now - datetime.timedelta(days=1)),
                ("Book dentist appointment",      False, now + datetime.timedelta(days=3)),
                ("Meal prep for the week",        False, now + datetime.timedelta(days=1)),
                ("Buy new running shoes",         False, None),
            ]),
            (ws(0), "Home Improvement", [
                ("Fix kitchen tap",               False, now + datetime.timedelta(days=7)),
                ("Repaint living room",           False, None),
                ("Order new bookshelf",           True,  now - datetime.timedelta(days=2)),
            ]),
            (ws(1), "Q2 Product Launch", [
                ("Write launch blog post",        False, now + datetime.timedelta(days=5)),
                ("Prepare demo video",            False, now + datetime.timedelta(days=4)),
                ("Send press release",            False, now + datetime.timedelta(days=6)),
                ("Update pricing page",           True,  now - datetime.timedelta(days=3)),
            ]),
            (ws(1), "Team Onboarding", [
                ("Set up new hire accounts",      True,  now - datetime.timedelta(days=5)),
                ("Schedule 1:1 meetings",         False, now + datetime.timedelta(days=2)),
                ("Create onboarding checklist",   False, None),
            ]),
            (ws(2), "Summer Vacation", [
                ("Book flights to Barcelona",     False, now + datetime.timedelta(days=14)),
                ("Reserve hotel",                 False, now + datetime.timedelta(days=14)),
                ("Pack suitcases",                False, now + datetime.timedelta(days=20)),
                ("Notify school about absence",   True,  now - datetime.timedelta(days=1)),
            ]),
            (ws(2), "Home Finances", [
                ("Review monthly budget",         False, now + datetime.timedelta(days=2)),
                ("Pay electricity bill",          False, now + datetime.timedelta(days=1)),
                ("Compare insurance plans",       False, None),
                ("File tax return",               True,  now - datetime.timedelta(days=10)),
            ]),
        ]

        # Extra projects for workspaces 3 and 4 if they exist
        if ws_count >= 4:
            projects_spec += [
                (ws(3), "Garden Project", [
                    ("Buy seeds",                 False, now + datetime.timedelta(days=2)),
                    ("Plant tomatoes",            False, now + datetime.timedelta(days=5)),
                    ("Set up irrigation",         True,  now - datetime.timedelta(days=3)),
                ]),
            ]
        if ws_count >= 5:
            projects_spec += [
                (ws(4), "Learning Goals", [
                    ("Finish Django course",      False, now + datetime.timedelta(days=10)),
                    ("Read Clean Code",           True,  now - datetime.timedelta(days=7)),
                    ("Practice Spanish 30 min/day", False, None),
                ]),
            ]

        for target_ws, project_name, tasks in projects_spec:
            project = Project.objects.create(name=project_name, workspace=target_ws)
            project.members.add(demo_user)
            for title, completed, due in tasks:
                Task.objects.create(
                    workspace=target_ws,
                    project=project,
                    title=title,
                    is_completed=completed,
                    due_datetime=due,
                )

        # ── Events ────────────────────────────────────────────────────────────
        events_spec = [
            (ws(0), "Yoga class",               now + datetime.timedelta(days=2),   now + datetime.timedelta(days=2, hours=1),          "Studio 4"),
            (ws(0), "Doctor check-up",          now + datetime.timedelta(days=5),   now + datetime.timedelta(days=5, hours=1),          "City Clinic"),
            (ws(1), "Q2 Kickoff Meeting",       now + datetime.timedelta(days=1),   now + datetime.timedelta(days=1, hours=2),          "Conference Room B"),
            (ws(1), "Product Demo",             now + datetime.timedelta(days=8),   now + datetime.timedelta(days=8, hours=1, minutes=30), "Online / Zoom"),
            (ws(2), "Family BBQ",               now + datetime.timedelta(days=3),   now + datetime.timedelta(days=3, hours=4),          "Grandma's garden"),
            (ws(2), "Parent-teacher meeting",   now + datetime.timedelta(days=6),   now + datetime.timedelta(days=6, hours=1),          "School hall"),
        ]
        for target_ws, title, start, end, location in events_spec:
            Event.objects.create(workspace=target_ws, title=title,
                                 start_time=start, end_time=end, location=location)

        # ── Reminders ─────────────────────────────────────────────────────────
        reminders_spec = [
            (ws(0), "Take vitamins",                now + datetime.timedelta(hours=8)),
            (ws(1), "Follow up with design team",   now + datetime.timedelta(days=1)),
            (ws(2), "Buy birthday cake for Mum",    now + datetime.timedelta(days=2)),
        ]
        for target_ws, message, due in reminders_spec:
            first_task = Task.objects.filter(workspace=target_ws).first()
            Reminder.objects.create(task=first_task, message=message,
                                    due_datetime=due, is_resolved=False)

        # ── QuickNotes ────────────────────────────────────────────────────────
        notes_spec = [
            (ws(0), "Shopping list",   "list",  "Milk\nEggs\nBread\nButter\nOlive oil\nApples"),
            (ws(1), "Meeting notes",   "plain", "Discussed Q2 roadmap. Key priorities: launch, onboarding, marketing push."),
            (ws(2), "Vacation packing","list",  "Passports\nSunscreen\nSandals\nChargers\nFirst aid kit\nCamera"),
        ]
        for target_ws, title, display_type, content in notes_spec:
            QuickNote.objects.create(user=demo_user, title=title,
                                     content=content, display_type=display_type,
                                     shared_workspace=target_ws)

        self.stdout.write(self.style.SUCCESS(
            f"Demo data created: {len(demo_workspaces)} workspaces, "
            f"{len(projects_spec)} projects."
        ))
