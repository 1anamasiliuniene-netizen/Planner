from django.db.models import Q

from .models import Reminder

DEMO_USERNAME = "demo"


def navbar_reminders(request):
    if not request.user.is_authenticated:
        return {"navbar_reminders": [], "navbar_reminder_count": 0, "is_demo": False}

    reminders_qs = (
        Reminder.objects.filter(
            Q(task__workspace__membership__user=request.user)
            | Q(event__workspace__membership__user=request.user),
            is_resolved=False,
        )
        .select_related("task", "event", "task__workspace", "event__workspace")
        .order_by("due_datetime")
        .distinct()
    )

    reminders = list(reminders_qs[:8])
    return {
        "navbar_reminders": reminders,
        "navbar_reminder_count": reminders_qs.count(),
        "is_demo": request.user.username == DEMO_USERNAME,
    }

