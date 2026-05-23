# Quickstart: Dynamic Role-Based Navigation System

## Developer Setup

1. **Verify Profiles**: Ensure you have at least one user with each profile type (Student, Teacher, Supervisor, Manager) for testing.
2. **Context Processor**: Verify that `'core.context_processors.nav_items'` is added to the `TEMPLATES` setting in `academy_project/settings.py`.
3. **Template Inheritance**: Ensure your template extends `base.html` to see the dynamic navigation.

## Testing the Navigation

### Manual Testing
1. Log in as a **Student**:
   - Verify you see links like "الملف الشخصي", "كورساتي", "المكتبة", etc.
   - Click a link and verify it highlights as active.
2. Log in as a **Teacher**:
   - Verify you see "لوحة تحكم المعلم", "رفع المواد", etc.
3. Log in as a **Supervisor**:
   - Verify you see "لوحة المشرف", "إدارة الطلاب", etc.
4. Log in as a **Manager**:
   - Verify you see "لوحة الإدارة" and "الإحصائيات".

### Automated Testing
Run the following command to verify the context processor logic:
```bash
pytest tests/test_navigation.py
```
*(Note: Create this test file during implementation)*

## Troubleshooting
- **Nav not appearing**: Ensure the template uses `{% extends "base.html" %}`.
- **Wrong links**: Check the mapping in `core/context_processors.py`.
- **Styling issues**: The navigation uses Tailwind CSS classes provided by `django-unfold`. Ensure `unfold` is correctly configured in `INSTALLED_APPS`.
