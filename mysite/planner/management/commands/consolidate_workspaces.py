"""
Management command: consolidate_workspaces
Merges "Family Shared" into "Family" for the real owner account.
"""
from django.core.management.base import BaseCommand
from planner.models import Workspace, Task, Project, Event, Membership
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Consolidate Family Shared workspace into Family"

    def handle(self, *args, **options):
        try:
            family = Workspace.objects.get(pk=5, name="Family")
            family_shared = Workspace.objects.get(pk=6, name="Family Shared")
        except Workspace.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Error: Workspace not found - {e}"))
            return

        self.stdout.write("\n=== Consolidating Workspaces ===\n")
        self.stdout.write(f"FROM: {family_shared.name} (id={family_shared.id})")
        self.stdout.write(f"TO:   {family.name} (id={family.id})\n")

        # Move projects
        proj_count = family_shared.projects.count()
        self.stdout.write(f"Moving {proj_count} projects...")
        for p in family_shared.projects.all():
            p.workspace = family
            p.save()
            self.stdout.write(f"  ✓ {p.name}")

        # Move tasks
        task_count = Task.objects.filter(workspace=family_shared).count()
        self.stdout.write(f"\nMoving {task_count} tasks...")
        Task.objects.filter(workspace=family_shared).update(workspace=family)

        # Move events
        event_count = Event.objects.filter(workspace=family_shared).count()
        self.stdout.write(f"Moving {event_count} events...")
        Event.objects.filter(workspace=family_shared).update(workspace=family)

        # Migrate members
        member_count = Membership.objects.filter(workspace=family_shared).count()
        self.stdout.write(f"\nMigrating {member_count} members...")
        for m in Membership.objects.filter(workspace=family_shared):
            Membership.objects.get_or_create(
                workspace=family,
                user=m.user,
                defaults={"role": m.role}
            )
            self.stdout.write(f"  ✓ {m.user.username}")

        # Delete Family Shared
        self.stdout.write(f"\nDeleting {family_shared.name}...")
        family_shared.delete()

        self.stdout.write(self.style.SUCCESS("\n✓ Consolidation Complete!\n"))

        # Verify
        final_proj = family.projects.count()
        final_task = Task.objects.filter(workspace=family).count()
        final_member = family.members.count()

        self.stdout.write(f"Final state - Family workspace:")
        self.stdout.write(f"  Projects: {final_proj}")
        self.stdout.write(f"  Tasks: {final_task}")
        self.stdout.write(f"  Members: {final_member}\n")

