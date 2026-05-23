import re
from functools import wraps
from django.core.exceptions import PermissionDenied

def check_device(request):
    """
    بسيطة للتحقق من نوع الجهاز (تجريبي)
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'mobile' in user_agent:
        return 'mobile'
    return 'desktop'

def has_group(user, group_name):
    """
    التحقق من انضمام المستخدم لمجموعة معينة
    """
    return user.groups.filter(name=group_name).exists()

def get_video_id(url):
    """
    يستخرج الـ ID الخاص بفيديو يوتيوب من الرابط
    """
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

def check_password_strength(password):
    """
    تحقق بسيط من قوة كلمة المرور
    """
    if len(password) < 8:
        return False, "يجب أن تكون كلمة المرور 8 أحرف على الأقل."
    return True, ""

# --- Role Management Helpers ---

def is_active_student(request):
    return request.user.is_authenticated and getattr(request, 'active_role', None) == 'student' and hasattr(request.user, 'student_profile')

def is_active_teacher(request):
    return request.user.is_authenticated and getattr(request, 'active_role', None) == 'teacher' and hasattr(request.user, 'teacher_profile')

def is_active_supervisor(request):
    return request.user.is_authenticated and getattr(request, 'active_role', None) == 'supervisor' and hasattr(request.user, 'supervisor_profile')

def is_active_manager(request):
    return request.user.is_authenticated and getattr(request, 'active_role', None) == 'manager' and (hasattr(request.user, 'manager_profile') or request.user.is_superuser)

def role_required(allowed_roles):
    """
    Decorator to restrict access based on the active session role.
    Usage: @role_required(['teacher', 'manager'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
                
            if getattr(request, 'active_role', None) in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied("ليس لديك صلاحية للوصول إلى هذه الصفحة بالدور الحالي.")
        return _wrapped_view
    return decorator
