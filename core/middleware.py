# core/middleware.py
from django.shortcuts import redirect
from django.contrib import messages

class AdminAccessRedirectMiddleware:
    """
    Redirects non-superusers away from /admin/ to the portal home page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is attempting to access any admin URL
        if request.path.startswith('/admin/'):
            # Allow completely unauthenticated users to see the login screen
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    messages.warning(
                        request, 
                        "Access restricted: Staff accounts do not have permission to access the Django admin portal."
                    )
                    # Redirect to your home page or portal landing route name
                    return redirect('/')  # or redirect('/')
        
        return self.get_response(request)