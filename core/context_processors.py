from django.urls import reverse, NoReverseMatch
from . import dashboard

NAV_CONFIG = {
    'STUDENT': [
        {'label': 'الملف الشخصي', 'url_name': 'core:profile_view', 'icon': 'fas fa-user-circle'},
        {'label': 'كورساتي', 'url_name': 'core:landing_page', 'icon': 'fas fa-graduation-cap'},
        {'label': 'المكتبة', 'url_name': 'core:academy_details', 'icon': 'fas fa-book-reader'},
        {'label': 'الاختبارات', 'url_name': 'quiz:quiz_dashboard', 'icon': 'fas fa-tasks'},
        {'label': 'الدردشة', 'url_name': 'core:chat_home', 'icon': 'fas fa-comments'},
        {'label': 'حصص الفيديو', 'url_name': 'core:video_call', 'icon': 'fas fa-video'},
    ],
    'TEACHER': [
        {'label': 'لوحة تحكم المعلم', 'url_name': 'core:landing_page', 'icon': 'fas fa-chalkboard-teacher'},
        {'label': 'رفع المواد', 'url_name': 'core:upload_material', 'icon': 'fas fa-file-upload'},
        {'label': 'الاختبارات', 'url_name': 'quiz:quiz_dashboard', 'icon': 'fas fa-plus-square'},
        {'label': 'التقارير اليومية', 'url_name': 'core:submit_daily_report', 'icon': 'fas fa-clipboard-list'},
        {'label': 'الدردشة', 'url_name': 'core:chat_home', 'icon': 'fas fa-comments'},
    ],
    'SUPERVISOR': [
        {'label': 'لوحة المشرف', 'url_name': 'core:supervisor_dashboard', 'icon': 'fas fa-user-shield'},
        {'label': 'متابعة الحضور', 'url_name': 'core:supervisor_dashboard', 'icon': 'fas fa-user-check'},
        {'label': 'إدارة الطلاب', 'url_name': 'core:admin_panel', 'icon': 'fas fa-users-cog'},
        {'label': 'الدردشة', 'url_name': 'core:chat_home', 'icon': 'fas fa-comments'},
    ],
    'MANAGER': [
        {'label': 'لوحة الإدارة', 'url_name': 'admin:index', 'icon': 'fas fa-cogs'},
        {'label': 'الإحصائيات', 'url_name': 'core:admin_panel', 'icon': 'fas fa-chart-line'},
        {'label': 'الدردشة', 'url_name': 'core:chat_home', 'icon': 'fas fa-comments'},
    ]
}

def nav_items(request):
    """
    Injects role-specific navigation items into the template context based on the active role.
    """
    if not request.user.is_authenticated:
        return {'nav_items': [], 'available_roles': []}

    user = request.user
    active_role = getattr(request, 'active_role', None)
    
    # Get all roles the user possesses
    possessed_roles = []
    if hasattr(user, 'student_profile'): possessed_roles.append('student')
    if hasattr(user, 'teacher_profile'): possessed_roles.append('teacher')
    if hasattr(user, 'supervisor_profile'): possessed_roles.append('supervisor')
    if hasattr(user, 'manager_profile') or user.is_superuser: possessed_roles.append('manager')

    # Map possesssed_roles to NAV_CONFIG keys
    active_nav_key = active_role.upper() if active_role else None
    
    items = []
    if active_nav_key and active_nav_key in NAV_CONFIG:
        for config_item in NAV_CONFIG[active_nav_key]:
            try:
                url = reverse(config_item['url_name'])
                items.append({
                    'label': config_item['label'],
                    'url': url,
                    'icon': config_item['icon']
                })
            except NoReverseMatch:
                # Handle special cases with arguments if needed
                if config_item['url_name'] == 'core:video_call':
                    try:
                        url = reverse('core:video_call', args=['general'])
                        items.append({
                            'label': config_item['label'],
                            'url': url,
                            'icon': config_item['icon']
                        })
                    except NoReverseMatch: pass
                continue

    return {
        'nav_items': items,
        'active_role': active_role,
        'available_roles': possessed_roles
    }

def unfold_dashboard(request):
    """Call the dashboard callback and return its context for templates.

    This makes the `kpi` data available to admin templates (and others).
    """
    try:
        context = dashboard.dashboard_callback(request, {}) or {}
    except Exception:
        # Fail safe: don't break page rendering if dashboard has an error
        context = {}
    return context
