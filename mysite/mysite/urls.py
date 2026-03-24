from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Planner app (includes all auth + password reset routes)
    path("", include("planner.urls")),
]