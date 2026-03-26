from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from planner.models import Membership, Project, Task, Workspace


class Command(BaseCommand):
    help = "Create demo data: 3 workspaces, projects, and checkable tasks."

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Username to seed data for")

    def handle(self, *args, **options):
        user = self._resolve_user(options.get("username"))

        plan = {
            "Personal": ["Home", "Health"],
            "Work": ["Client A", "Internal"],
            "Family": ["Kids", "Parents"],
        }

        created_tasks = 0
        for workspace_name, project_names in plan.items():
            workspace, _ = Workspace.objects.get_or_create(
                name=workspace_name,
                defaults={"type": workspace_name.lower()},
            )
            Membership.objects.get_or_create(
                user=user,
                workspace=workspace,
                defaults={"role": "owner"},
            )

            for project_name in project_names:
                project, _ = Project.objects.get_or_create(
                    workspace=workspace,
                    name=project_name,
                )
                project.members.add(user)

                for idx in range(1, 4):
                    title = f"{project_name} task {idx}"
                    due_date = timezone.now() + timedelta(days=idx)
                    task, created = Task.objects.get_or_create(
                        workspace=workspace,
                        project=project,
                        title=title,
                        defaults={
                            "description": f"Auto-generated task for {project_name}",
                            "due_date": due_date,
                            "priority": idx,
                            "is_completed": idx == 3,
                        },
                    )
                    if created:
                        created_tasks += 1

        self.stdout.write(self.style.SUCCESS(f"Seed completed for user '{user.username}'."))
        self.stdout.write(self.style.SUCCESS(f"Created {created_tasks} new tasks."))

    def _resolve_user(self, username):
        User = get_user_model()
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f"User '{username}' does not exist.") from exc

        user = User.objects.order_by("id").first()
        if not user:
            raise CommandError("No users found. Create a user first.")
        return user

