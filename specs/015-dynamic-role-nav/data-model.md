# Data Model: Dynamic Role-Based Navigation System

## NavItem Schema (Internal Context Processor Structure)

The `nav_items` list injected by the context processor contains `NavItem` dictionaries with the following schema:

| Field | Type | Description |
|-------|------|-------------|
| `label` | `str` | The display name of the navigation item (Arabic/English). |
| `url` | `str` | The absolute URL path or resolved Django URL. |
| `icon` | `str` | The FontAwesome CSS classes (e.g., `fas fa-user`). |
| `active` | `bool` | True if the current request path matches this item's URL. |

### Role Definitions (Internal Constants)

Roles are identified based on profile attributes:
- `STUDENT`: `hasattr(user, 'student_profile')`
- `TEACHER`: `hasattr(user, 'teacher_profile')`
- `SUPERVISOR`: `hasattr(user, 'supervisor_profile')`
- `MANAGER`: `hasattr(user, 'manager_profile')`

## Navigation Mapping Configuration (Logic)

The mapping of roles to items is defined as follows:

```python
NAV_CONFIG = {
    'STUDENT': [
        {'label': 'الملف الشخصي', 'url_name': 'core:profile_view', 'icon': 'fas fa-user-circle'},
        {'label': 'كورساتي', 'url_name': 'core:landing_page', 'icon': 'fas fa-graduation-cap'},
        {'label': 'المكتبة', 'url_name': 'core:academy_details', 'icon': 'fas fa-book-reader'},
        {'label': 'الاختبارات', 'url_name': 'quiz:take_quiz', 'icon': 'fas fa-tasks'},
        {'label': 'الدردشة', 'url_name': 'core:chat_home', 'icon': 'fas fa-comments'},
        {'label': 'حصص الفيديو', 'url_name': 'core:video_call', 'icon': 'fas fa-video'},
    ],
    'TEACHER': [
        {'label': 'لوحة تحكم المعلم', 'url_name': 'core:landing_page', 'icon': 'fas fa-chalkboard-teacher'},
        {'label': 'رفع المواد', 'url_name': 'core:upload_material', 'icon': 'fas fa-file-upload'},
        {'label': 'إنشاء اختبار', 'url_name': 'quiz:create_quiz', 'icon': 'fas fa-plus-square'},
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
    ]
}
```

## Template Data Model (Injected Context)

- `nav_items`: `List[NavItem]` (List of items relevant to the current user's role).
- `user_roles`: `List[str]` (List of identified roles for the current user).
