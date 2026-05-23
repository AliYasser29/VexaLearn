class RoleContextMiddleware:
    """
    Middleware to inject the 'active_role' into the request object.
    This allows the application to handle multi-role users by maintaining
    an active context in the session.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check session for active role
            active_role = request.session.get('active_role')
            
            # If not in session, try to get from default_role or fallback to first available
            if not active_role:
                try:
                    profile = request.user.unified_profile
                    active_role = profile.default_role
                except:
                    active_role = None

            # Fallbacks if session and default_role are empty
            if not active_role:
                if hasattr(request.user, 'manager_profile') or request.user.is_superuser:
                    active_role = 'manager'
                elif hasattr(request.user, 'supervisor_profile'):
                    active_role = 'supervisor'
                elif hasattr(request.user, 'teacher_profile'):
                    active_role = 'teacher'
                elif hasattr(request.user, 'student_profile'):
                    active_role = 'student'
                
                if active_role:
                    request.session['active_role'] = active_role

            # Inject active_role into request
            request.active_role = active_role
        else:
            request.active_role = None
        
        response = self.get_response(request)
        return response

from django.conf import settings

class MediaCacheMiddleware:
    """
    Middleware to inject Cache-Control headers for /media/ responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(getattr(settings, 'MEDIA_URL', '/media/')):
            response['Cache-Control'] = 'public, max-age=31536000' # Cache for 1 year
        return response

from django.shortcuts import redirect
from django.contrib import messages

class RoleAccessMiddleware:
    """
    Strict Role-Based Access Control Middleware.
    Blocks users from accessing paths they do not have the active role for.
    Must be placed after RoleContextMiddleware in settings.py.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            active_role = getattr(request, 'active_role', None)

            # Restrict access to Student dashboard
            if path.startswith('/dashboard/student/') and active_role != 'student':
                messages.error(request, "Access Denied: You must be a student to view this page.")
                return redirect('login')
            
            # Restrict access to Instructor dashboard
            if path.startswith('/dashboard/instructor/') and active_role != 'teacher':
                messages.error(request, "Access Denied: You must be an instructor to view this page.")
                return redirect('login')
            
            # Restrict access to Supervisor dashboard (exact match since it is /dashboard/)
            if path == '/dashboard/' and active_role not in ['supervisor', 'manager']:
                messages.error(request, "Access Denied: You do not have supervisor access.")
                return redirect('login')

            # Restrict access to Admin panel
            if path.startswith('/admin/') and not (request.user.is_superuser or active_role == 'manager'):
                messages.error(request, "Access Denied: Admin access required.")
                return redirect('login')

        response = self.get_response(request)
        return response
