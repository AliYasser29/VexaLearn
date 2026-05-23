---
description: "Task list for Dynamic Role-Based Navigation System implementation"
---

# Tasks: Dynamic Role-Based Navigation System

**Input**: Design documents from `/specs/015-dynamic-role-nav/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Tests are included to verify the context processor logic and active state detection.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Create `core/templatetags/` directory and `core/templatetags/__init__.py`
- [x] T002 [P] Create `templates/` directory at the project root for global overrides
- [x] T003 [P] Verify `django-unfold` and `font-awesome` are listed in `requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for the navigation system

**⚠️ CRITICAL**: This phase must be completed before starting any user story work.

- [x] T004 Define the role-to-navigation mapping constant in `core/context_processors.py` based on `data-model.md`
- [x] T005 Implement the basic `nav_items` context processor function in `core/context_processors.py` that returns an empty list for now
- [x] T006 Register `core.context_processors.nav_items` in the `TEMPLATES` setting in `academy_project/settings.py`
- [x] T007 [P] Create `core/templatetags/nav_tags.py` with a placeholder `is_active` template tag
- [x] T008 Create `templates/base.html` extending `unfold/layouts/base.html` and include Cairo font and FontAwesome in the `extrahead` block

**Checkpoint**: Foundation ready - the context processor is active and the base template exists.

---

## Phase 3: User Story 1 - Role-Specific Navigation (Priority: P1) 🎯 MVP

**Goal**: Automatically display role-relevant navigation links for Student, Teacher, Supervisor, and Manager.

**Independent Test**: Log in as a Student and verify `nav_items` in the template context contains "My Courses", "Library", etc.

### Tests for User Story 1

- [x] T009 [P] [US1] Create `tests/test_navigation.py` and implement unit tests for the `nav_items` context processor with mocked users/profiles

### Implementation for User Story 1

- [x] T010 [US1] Implement profile detection logic in `core/context_processors.py` using `hasattr(user, 'student_profile')`, etc.
- [x] T011 [US1] Update `nav_items` in `core/context_processors.py` to filter and return the correct items from the mapping based on detected roles
- [x] T012 [US1] Add sidebar rendering logic to `templates/base.html` using a `{% for item in nav_items %}` loop
- [x] T013 [US1] Implement `django-unfold` sidebar item styling in `templates/base.html` (using Tailwind classes like `flex items-center`)
- [x] T014 [US1] Ensure `nav_items` handles users with no profiles or anonymous users gracefully (returning empty list or default)

**Checkpoint**: User Story 1 is functional - roles see their respective menus.

---

## Phase 4: User Story 2 - Navigation Active State (Priority: P2)

**Goal**: Highlight the navigation button of the current active page.

**Independent Test**: Navigate to the Profile page and verify the "Profile" sidebar item has the active CSS class/style.

### Tests for User Story 2

- [x] T015 [P] [US2] Add a test case to `tests/test_navigation.py` to verify the `is_active` tag logic against different request paths

### Implementation for User Story 2

- [x] T016 [US2] Implement the logic in `core/templatetags/nav_tags.py` to check if the current request path starts with or matches the item URL
- [x] T017 [US2] Update the sidebar loop in `templates/base.html` to load `nav_tags` and use the `is_active` tag to apply conditional CSS classes
- [x] T018 [US2] Add the `active` visual style (e.g., `bg-primary-500 text-white`) to the sidebar items in `templates/base.html`

**Checkpoint**: User Story 2 is functional - the current page is highlighted in the menu.

---

## Phase 5: User Story 3 - Global Availability & Responsiveness (Priority: P3)

**Goal**: Ensure navigation is present on all pages and works on mobile devices.

**Independent Test**: Open the Profile page on a mobile viewport and verify the sidebar is collapsible/accessible via a menu button.

### Implementation for User Story 3

- [x] T019 [US3] Implement the responsive mobile menu toggle in `templates/base.html` following `django-unfold` layout patterns
- [x] T020 [US3] Update `core/templates/core/profile.html` to extend `base.html` and remove duplicated CSS/JS links
- [x] T021 [US3] Update `core/templates/core/landing_page.html` to extend `base.html`
- [x] T022 [US3] Update `core/templates/core/supervisor_dashboard.html` to extend `base.html`
- [x] T023 [US3] Update `core/templates/core/admin_panel.html` to extend `base.html`
- [x] T024 [US3] Verify navigation visibility on `quiz/` related templates (e.g., `take_quiz.html`)

**Checkpoint**: All major pages now use the global dynamic navigation.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and verification

- [x] T025 [P] Ensure the Cairo font is correctly applied to all navigation elements via `templates/base.html`
- [x] T026 [P] Verify that FontAwesome icons match the role-mapping specified in `data-model.md`
- [x] T027 [P] Perform a final manual walk-through of all 4 roles to confirm navigation correctness
- [x] T028 [P] Run all tests in `tests/test_navigation.py` to ensure no regressions
- [x] T029 [P] Update `Readme.md` or internal docs if navigation configuration needs to be documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1. BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Phase 2.
  - US1 (Phase 3) is the MVP and should be completed first.
  - US2 and US3 can proceed in parallel once US1 is foundational.

### User Story Dependencies

- **User Story 1 (P1)**: Foundation for all UI-based navigation.
- **User Story 2 (P2)**: Enhancement to US1 UI.
- **User Story 3 (P3)**: Extension of the system to all pages.

### Parallel Opportunities

- T001, T002, T003 can be done in parallel.
- T007 (Templatetags setup) can be done in parallel with T004-T005.
- Once T012 is done (Base template loop), US2 (Active state) and US3 (Mobile/Refactoring) can start.

---

## Parallel Example: User Story 1

```bash
# Developer A:
Task T010: Implement profile detection in core/context_processors.py
Task T011: Filter nav_items in core/context_processors.py

# Developer B:
Task T012: Add sidebar rendering loop in templates/base.html
Task T013: Style sidebar items in templates/base.html
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Implement US1: Role detection and basic menu rendering.
3. Validate that different users see different menus.

### Incremental Delivery

1. Add Active State highlighting (US2).
2. Refactor existing templates to use the new global `base.html` (US3).
3. Final polish and verification.

---

## Notes

- All tasks follow the `[ID] [P?] [Story] Description` format.
- File paths are explicitly mentioned for each task.
- Each user story is designed to be independently testable.
