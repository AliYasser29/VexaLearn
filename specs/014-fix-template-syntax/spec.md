# Feature Specification: Comprehensive Template Syntax Audit & Remediation

**Feature Branch**: `014-fix-template-syntax`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: User description: "Conduct a comprehensive audit and remediation of all Django TemplateSyntaxErrors across the entire VexaLearn project..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Landing Page Loads Without Operator Error (Priority: P1) 🎯 MVP

When any visitor navigates to the landing page (`/`) and selects a country to filter academies, the page must render correctly. Currently `selected_country_id==country.id` in the template tag causes a `TemplateSyntaxError` due to a missing space around the `==` operator.

**Why this priority**: The landing page is the entry point for all public users. A crash here blocks 100% of traffic.

**Independent Test**: Navigate to `/` and use the country dropdown filter; the page must not return a 500 error and must display academies.

**Acceptance Scenarios**:

1. **Given** any visitor is on the landing page, **When** they select a country filter, **Then** the page filters and reloads without a 500 error.
2. **Given** `selected_country_id == country.id` uses correct spacing, **When** the template engine processes the tag, **Then** the comparison evaluates correctly.

---

### User Story 2 - Supervisor Dashboard Renders Correctly (Priority: P1)

Supervisors and superusers cannot access `/dashboard/` at all because `supervisor_dashboard.html` contains a structural `{% empty %}` tag on line 556 that is nested inside an `{% if %}` block (not a `{% for %}` block), causing a `TemplateSyntaxError`. The forloop structure inside the enrollments `td` is also misindented.

**Why this priority**: This is the primary workspace for all supervisors. A crash here makes the product non-functional for staff.

**Independent Test**: Log in as a supervisor and navigate to `/dashboard/`. The student table with all course cards, attendance buttons, and teacher badges must render correctly.

**Acceptance Scenarios**:

1. **Given** a logged-in supervisor, **When** they visit `/dashboard/`, **Then** the page renders without any `TemplateSyntaxError`.
2. **Given** students have enrollments, **When** the dashboard renders, **Then** each enrollment's course card shows attendance progress, action buttons and archive status correctly.

---

### User Story 3 - Universal Chat Monitor Operator Fix (Priority: P2)

The universal chat monitor at `/monitor/` uses `user1_id==u.id` and `user2_id==u.id` comparisons in template tags without spaces, which will produce `TemplateSyntaxError` when rendered.

**Why this priority**: Affects monitoring capabilities for admin/superusers but not critical to regular user flows.

**Independent Test**: Log in as a superuser and navigate to `/monitor/`, select two users and verify the chat log displays.

**Acceptance Scenarios**:

1. **Given** a superuser at the monitor page, **When** they select users from the dropdowns, **Then** the previously selected option remains highlighted without a 500 error.

---

### Edge Cases

- Operator spacing fixes must only target Django template tags (`{% if ... %}`), not JavaScript code which legitimately uses `===`, `==` etc.
- The `{% empty %}` tag is valid only as a clause inside a `{% for %}` block. Any `{% empty %}` inside an `{% if %}` block must be replaced with `{% else %}`.
- All `{% for %}` loops must have matching `{% endfor %}` and all `{% if %}` blocks must close with `{% endif %}`.
- Quiz templates may also reference `{% static %}` or have similar issues and must be scanned.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All Django template tag operator comparisons (==, !=, <, >, <=, >=) MUST have spaces around the operator.
- **FR-002**: The `{% empty %}` tag MUST only appear as a clause inside `{% for %}` blocks, never inside `{% if %}` blocks.
- **FR-003**: All `{% if %}` and `{% for %}` blocks MUST be properly closed with their matching `{% endif %}` and `{% endfor %}` tags.
- **FR-004**: The `supervisor_dashboard.html` enrollment `for` loop structure MUST be corrected so the `{% empty %}` for the enrollment loop appears at the correct nesting level.
- **FR-005**: All templates using `{% static %}` MUST include `{% load static %}` at the top (already fixed in feature 013, included here for completeness).
- **FR-006**: The fix MUST target only Django template tag syntax — JavaScript equality operators (`===`, `==`) within `<script>` blocks MUST NOT be modified.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All public-facing URLs (`/`, `/dashboard/`, `/monitor/`, `/profile/`, `/chat/`, login pages) return HTTP 200 or expected redirects with zero 500 errors.
- **SC-002**: `python manage.py check` reports zero issues after remediation.
- **SC-003**: The Django development server log shows zero `TemplateSyntaxError` entries during a full navigation of all routes.
- **SC-004**: All template conditional logic (filters, selections, country dropdowns) functions correctly — previously-selected options remain highlighted.

## Assumptions

- JavaScript inside `<script>` tags is not subject to Django's template parser and does not need operator-spacing fixes.
- The `quiz/templates/` directory does not currently contain templates with these specific syntax issues (confirmed by scan; no `{% if x==y %}` patterns found there).
- The `supervisor_dashboard.html` `{% empty %}` on line 556 belongs to the inner `{% for enrollment in student.enrollment_set.all %}` loop which closed on line 555 (`</div>`), not to the outer `{% for student in students %}` loop.
- No template uses `{% extends %}`, so `{% load static %}` placement at line 1 is correct.
