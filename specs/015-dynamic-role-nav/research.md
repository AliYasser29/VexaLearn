# Research: Dynamic Role-Based Navigation System

## Overview
The goal is to implement a global navigation system that dynamically displays links based on the user's role (Student, Teacher, Supervisor, or Manager) in a way that is consistent with the `django-unfold` aesthetic and integrated into all major front-end templates.

## 1. Role Identification & URL Mapping

The identification of roles is based on the existence of specific profile relationships on the `User` model (`related_name`).

### Role Mapping Tables

| Role | Req. Label | Target URL Name | Required FontAwesome Icon |
|------|------------|-----------------|---------------------------|
| **Student** | Profile | `core:profile_view` | `fas fa-user-circle` |
| | My Courses | `core:landing_page` | `fas fa-graduation-cap` |
| | Library | `core:academy_details` | `fas fa-book-reader` |
| | Quizzes | `quiz:take_quiz` | `fas fa-tasks` |
| | Chat | `core:chat_home` | `fas fa-comments` |
| | Video Classes | `core:video_call` | `fas fa-video` |
| **Teacher** | Teacher Dashboard | `core:landing_page` | `fas fa-chalkboard-teacher` |
| | Upload Material | `core:upload_material` | `fas fa-file-upload` |
| | Create Quiz | `quiz:create_quiz` | `fas fa-plus-square` |
| | Daily Reports | `core:submit_daily_report` | `fas fa-clipboard-list` |
| | Chat | `core:chat_home` | `fas fa-comments` |
| **Supervisor** | Supervisor Dashboard | `core:supervisor_dashboard` | `fas fa-user-shield` |
| | Attendance Tracking | `core:supervisor_dashboard` | `fas fa-user-check` |
| | Student Management | `core:admin_panel` | `fas fa-users-cog` |
| | Chat | `core:chat_home` | `fas fa-comments` |
| **Manager** | Admin Panel | `admin:index` | `fas fa-cogs` |
| | Analytics | `core:admin_panel` | `fas fa-chart-line` |

## 2. Dynamic `nav_items` Structure
The context processor will inject a list of dictionary items into the global context:

```python
nav_items = [
    {
        "label": "Profile",
        "url": reverse("core:profile_view"),
        "icon": "fas fa-user-circle",
        "active": True/False (computed based on current path)
    },
    ...
]
```

## 3. Base Template Design
The new `base.html` will be created at `templates/base.html` (or modified if it exists, currently it seems to be missing).
It will extend `unfold/layouts/base.html` to leverage its styling and responsive layout, but will include a custom sidebar/navbar to render `nav_items`.

### Refactoring Strategy
1. Create `templates/base.html` extending `unfold/layouts/base.html`.
2. Move common headers (Cairo font, FontAwesome, `global_ux.css`) to the base template.
3. Update `core/templates/core/profile.html`, `landing_page.html`, etc., to extend this new `base.html`.

## 4. UI/UX Consistency
The design will strictly follow `django-unfold` components:
- Sidebars with Tailwind CSS classes (as `django-unfold` uses Tailwind).
- Arabic (RTL) support.
- Responsive toggles for mobile view.

## 5. Security & RBAC
Views will continue to be protected by role-based decorators (e.g., `@user_passes_test`). Hiding the link in the nav is a UI enhancement, not a security control.

## 6. Needs Clarification / Decisions
- **Decision**: For URLs requiring IDs (like `take_quiz` or `academy_details`), the context processor will provide "entry points" or general links if specific IDs aren't available globally. For example, "Library" might link to a general list of academies if no specific one is associated.
- **Decision**: If a user has multiple roles, the items from all roles will be combined and duplicates (e.g., "Chat") will be removed.
- **Decision**: The active state will be handled by a custom template tag that compares the current request path with the item's URL.
