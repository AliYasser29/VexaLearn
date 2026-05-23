# Feature Specification: Fix Template Inheritance and Missing CSS

**Feature Branch**: `016-fix-template-inheritance`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "Fix broken Django template inheritance and missing CSS. A previous automated refactor likely placed '{% load static %}' BEFORE the '{% extends ... %}' tag in multiple templates, causing Django to break the inheritance tree and drop the base CSS. 1) Scan all HTML files in 'core/templates/' and 'quiz/templates/'. 2) Enforce the strict Django rule: If a template uses '{% extends %}', it MUST be the absolute first line in the file (Line 1). 3) Move any '{% load static %}' tags to be immediately AFTER the '{% extends %}' tag. 4) Verify that the main base template (e.g., 'base.html' or similar) correctly includes the '<link rel=\"stylesheet\" href=\"{% static ... %}\">' tags. This will restore the UI globally."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fix Template Tag Order (Priority: P1)

As a developer, I want to ensure that `{% extends %}` is always the first line in templates so that Django's template inheritance works correctly and the base structure is preserved.

**Why this priority**: Correct tag ordering is critical for Django's template engine to process inheritance. If `{% extends %}` is not the first tag, the inheritance chain breaks, leading to missing headers, footers, and global styles.

**Independent Test**: Can be fully tested by verifying that any template using `{% extends %}` has it on Line 1, and the resulting rendered page includes the parent template's structure.

**Acceptance Scenarios**:

1. **Given** a template with `{% load static %}` on Line 1 and `{% extends "..." %}` on Line 2, **When** the fix is applied, **Then** `{% extends "..." %}` should be on Line 1 and `{% load static %}` should be on Line 2.
2. **Given** a template with multiple `{% load ... %}` tags before `{% extends %}`, **When** the fix is applied, **Then** all `{% load ... %}` tags should be moved below Line 1.

---

### User Story 2 - Ensure Static Files are Loaded (Priority: P2)

As a developer, I want to ensure `{% load static %}` is correctly placed after `{% extends %}` so that static assets (CSS, JS, images) can be referenced within the template without "TemplateSyntaxError" or missing assets.

**Why this priority**: Static assets are essential for the UI. If `{% load static %}` is removed or incorrectly placed during the refactor, the page will fail to load styling and interactivity.

**Independent Test**: Can be tested by checking if `{% static ... %}` tags inside the template resolve correctly without errors when the page is rendered.

**Acceptance Scenarios**:

1. **Given** a fixed template, **When** a CSS file is referenced via `{% static %}`, **Then** the link should be correctly generated in the HTML output.

---

### User Story 3 - Restore Global UI Styling (Priority: P3)

As a user, I want the application's CSS to load correctly across all pages so that the UI is visually consistent, usable, and professional.

**Why this priority**: This delivers the ultimate value to the end user. Restoring the CSS fix the broken layouts and restores the intended user experience.

**Independent Test**: Can be tested by navigating through various pages (Profile, Dashboard, Quizzes) and visually confirming that the `django-unfold` and custom styling are active.

**Acceptance Scenarios**:

1. **Given** the fixed inheritance tree, **When** any page is visited, **Then** the global stylesheet linked in `base.html` should be present in the `<head>` of the rendered page.

### Edge Cases

- **Templates without extends**: Some templates might be standalone or partials. These should only have `{% load static %}` at the top and should not be forced to have an `extends` tag if they didn't have one.
- **Comments at the top**: If there are HTML or Django comments at the very top, `{% extends %}` must still come before them according to strict Django rules.
- **Multiple extends tags**: A rare error, but the fix should only ensure the *first* valid `extends` tag is at Line 1.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST scan all `.html` files recursively in `core/templates/` and `quiz/templates/`.
- **FR-002**: System MUST identify templates containing the `{% extends %}` tag.
- **FR-003**: System MUST ensure that `{% extends %}` is the first non-empty line in the file.
- **FR-004**: System MUST move any `{% load static %}` tags to the line immediately following `{% extends %}`.
- **FR-005**: System MUST verify that the primary base template (identified as the target of most `extends` tags) contains valid `<link rel="stylesheet">` tags using the `{% static %}` tag.
- **FR-006**: System MUST NOT introduce duplicate `{% extends %}` or `{% load static %}` tags if they already exist in the correct locations.

### Key Entities *(include if feature involves data)*

- **Django Template**: An HTML file utilizing the Django Template Language (DTL).
- **Base Template**: The top-level template (e.g., `templates/base.html`) providing the shared layout and CSS links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of application pages display the shared layout (header, footer, navigation) defined in the parent template.
- **SC-002**: 0 runtime errors or layout breaks encountered when rendering views across the `core` and `quiz` modules.
- **SC-003**: 100% of application views correctly load and display the intended visual styling and brand assets.

## Assumptions

- The project uses standard Django template tags (`extends`, `load static`).
- The primary cause of missing CSS is the broken inheritance tree caused by incorrect tag placement.
- All target templates are within `core/templates/` and `quiz/templates/`.
- The `django-unfold` base template is also considered in the inheritance verification.
