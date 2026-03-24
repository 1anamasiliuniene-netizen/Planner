from django.contrib import admin
from .models import Workspace, Membership, Task, Event, Reminder

admin.site.register(Workspace)
admin.site.register(Membership)
admin.site.register(Task)
admin.site.register(Event)
admin.site.register(Reminder)


