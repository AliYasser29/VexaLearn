# Feature Specification: Fix Missing {% load static %} in Templates

**Feature Branch**: `013-fix-load-static`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "Fix the global TemplateSyntaxError 'Invalid block tag: static' occurring across multiple pages..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolve Dashboard TemplateSyntaxError (Priority: P1) 🎯 MVP

Any authenticated user who navigates to `/dashboard/` currently sees a Django `TemplateSyntaxError` (500 error) because `supervisor_dashboard.html` references `{% static %}` without first loading the tag library. This fix ensures the page renders correctly.

**Why this priority**: This is a P1 crash-level regression that prevents ALL users from accessing their dashboard, making the app non-functional.

**Independent Test**: Log in as a supervisor/superuser and navigate to `/dashboard/`. The page must render without a 500 error.

**Acceptance Scenarios**:

1. **Given** a logged-in supervisor, **When** they visit `/dashboard/`, **Then** the page loads with all CSS/JS assets served correctly via `{% static %}`.
2. **Given** an anonymous user, **When** they visit `/dashboard/`, **Then** they are redirected to the login page (not a 500 error).

---

### User Story 2 - Resolve TemplateSyntaxError Across All Pages (Priority: P1)

Eight other templates (`profile.html`, `chat.html`, `video_call.html`, `landing_page.html`, `public_login.html`, `management_login.html`, `superuser_login.html`, `course_materials.html`, `universal_chat_monitor.html`) all share the same missing `{% load static %}` declaration and will fail identically on first load.

**Why this priority**: Identical critical defect affecting all major user-facing routes. Must be fixed in the same pass.

**Independent Test**: Navigate to each affected URL and confirm the page renders without a 500 error and all linked assets load.

**Acceptance Scenarios**:

1. **Given** any affected template is rendered, **When** the Django template engine processes it, **Then** no `TemplateSyntaxError: Invalid block tag 'static'` is raised.
2. **Given** `{% load static %}` is added to all templates, **When** the server restarts, **Then** all routes return HTTP 200 (or correct redirect codes) with assets loading.

---

### Edge Cases

- Templates that use `{% extends %}` must have `{% load static %}` on the very first line or immediately after the extends tag (Django requires this).
- Since none of these templates currently extend a base template, `{% load static %}` is injected as the first line of each file.
- The `quiz/templates/` directory must also be scanned and fixed if applicable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render `/dashboard/` without a `TemplateSyntaxError`.
- **FR-002**: All templates using `{% static %}` MUST declare `{% load static %}` at the top.
- **FR-003**: Templates that use `{% extends %}` MUST place `{% load static %}` immediately after the extends tag.
- **FR-004**: The fix MUST NOT modify any HTML structure, CSS, or JavaScript logic — only add the missing tag library declaration.
- **FR-005**: All affected templates in `core/templates/` and `quiz/templates/` MUST be scanned and patched in a single pass.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 10 affected core templates render at their respective URLs with HTTP 200 (or expected redirect) and no 500 errors.
- **SC-002**: The Django development server starts and serves requests without any `TemplateSyntaxError` in the logs.
- **SC-003**: All `{% static %}` references resolve to correct file paths with no 404s for CSS/JS assets.
- **SC-004**: Zero regressions — other pages not in this fix scope continue to function identically.

## Assumptions

- No template in scope currently uses `{% extends %}`, so `{% load static %}` is safe to inject as the very first line.
- The `quiz/templates/` directory does not contain templates using `{% static %}` (confirmed by scan), so no changes needed there.
- The server must be restarted after changes for Django's template cache to invalidate.
