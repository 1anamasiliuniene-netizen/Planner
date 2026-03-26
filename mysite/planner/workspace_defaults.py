"""
Shared utility: create the 4 default workspaces for any user.
Used by signup view AND create_demo_data management command.
"""
import os
import shutil

from django.conf import settings

from planner.models import Workspace, Membership

# (name, type, default image filename)
DEFAULT_WORKSPACES = [
    ("Health",   "personal", "health.jpg"),
    ("Personal", "personal", "personal.jpg"),
    ("Work",     "work",     "work.jpg"),
    ("Family",   "family",   "family.jpg"),
]

DEFAULTS_DIR = os.path.join(settings.MEDIA_ROOT, "workspace_images", "defaults")


def create_default_workspaces(user, image_prefix=""):
    """
    Create 4 default workspaces for *user*, each with a copy of the
    seed image.  Returns the list of created Workspace objects.

    image_prefix -- optional string prepended to the copied filename
                    (e.g. "demo_" for the demo account).
    """
    created = []
    for name, ws_type, img_filename in DEFAULT_WORKSPACES:
        # Copy the seed image so every user gets their own file
        image_field_value = ""
        src = os.path.join(DEFAULTS_DIR, img_filename)
        if os.path.exists(src):
            slug = name.lower().replace(" ", "_")
            dest_name = f"workspace_images/{image_prefix}{slug}.jpg"
            dest = os.path.join(settings.MEDIA_ROOT, dest_name)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            image_field_value = dest_name

        ws = Workspace.objects.create(
            name=name,
            type=ws_type,
            image=image_field_value,
        )
        Membership.objects.create(workspace=ws, user=user, role="admin")
        created.append(ws)
    return created

