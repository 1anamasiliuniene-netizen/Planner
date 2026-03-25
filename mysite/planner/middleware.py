from django.contrib import messages
from django.shortcuts import redirect

DEMO_USERNAME = "demo"

# URL prefixes that demo user is allowed to POST to (read-only exceptions)
DEMO_ALLOWED_POSTS = {
    "/accounts/logout/",
    "/demo/login/",
}


class DemoReadOnlyMiddleware:
    """Block all POST/PUT/PATCH/DELETE requests for the demo user."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method in ("POST", "PUT", "PATCH", "DELETE")
            and request.user.is_authenticated
            and request.user.username == DEMO_USERNAME
            and request.path not in DEMO_ALLOWED_POSTS
        ):
            messages.warning(
                request,
                "This is a read-only demo account. "
                '<a href="/accounts/signup/" class="alert-link">Sign up</a> to make changes.',
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))

        return self.get_response(request)

