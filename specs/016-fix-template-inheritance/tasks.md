---
description: "Task list for Fix Template Inheritance and Missing CSS implementation"
---

# Tasks: Fix Template Inheritance and Missing CSS

**Input**: Design documents from `/specs/016-fix-template-inheritance/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Verification via shell commands and Django system check.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Project initialization and basic verification

- [x] T001 Verify all target directories exist: `core/templates/`, `quiz/templates/`, `templates/`

---

## Phase 2: Foundational

**Purpose**: Shared infrastructure (Not applicable for this feature)

*No foundational tasks required.*

---

## Phase 3: User Story 1 - Fix Template Tag Order (Priority: P1)

**Goal**: Ensure `{% extends %}` is always the first line in templates.

**Independent Test**: Run `grep -rn "{% extends" core/templates/ quiz/templates/ | grep -v ":1:"` and verify no results.

### Implementation for User Story 1

- [x] T002 [US1] Fix `{% extends %}` placement in `core/templates/core/admin_panel.html` (Ensure Line 1)
- [x] T003 [US1] Fix `{% extends %}` placement in `core/templates/core/landing_page.html` (Ensure Line 1)
- [x] T004 [US1] Fix `{% extends %}` placement in `core/templates/core/profile.html` (Ensure Line 1)
- [x] T005 [US1] Fix `{% extends %}` placement in `core/templates/core/supervisor_dashboard.html` (Ensure Line 1)
- [x] T006 [P] [US1] Scan remaining templates in `core/templates/` for misplaced `{% extends %}` tags
- [x] T007 [P] [US1] Scan all templates in `quiz/templates/` for misplaced `{% extends %}` tags

**Checkpoint**: User Story 1 is functional - template inheritance is structurally sound.

---

## Phase 4: User Story 2 - Ensure Static Files are Loaded (Priority: P2)

**Goal**: Ensure `{% load static %}` is correctly placed after `{% extends %}`.

**Independent Test**: Verify `{% static ... %}` tags render without syntax errors in the browser.

### Implementation for User Story 2

- [x] T008 [US2] Position `{% load static %}` on Line 2 in `core/templates/core/admin_panel.html`
- [x] T009 [US2] Position `{% load static %}` on Line 2 in `core/templates/core/landing_page.html`
- [x] T010 [US2] Position `{% load static %}` on Line 2 in `core/templates/core/profile.html`
- [x] T011 [US2] Position `{% load static %}` on Line 2 in `core/templates/core/supervisor_dashboard.html`
- [x] T012 [P] [US2] Ensure all templates using `{% static %}` tags have `{% load static %}` in `core/templates/`
- [x] T013 [P] [US2] Ensure all templates using `{% static %}` tags have `{% load static %}` in `quiz/templates/`

**Checkpoint**: User Story 2 is functional - static assets are properly referenced.

---

## Phase 5: User Story 3 - Restore Global UI Styling (Priority: P3)

**Goal**: Restore global UI styling by linking `global_ux.css` in the base template.

**Independent Test**: Visually confirm `global_ux.css` is applied to the landing page and profile page.

### Implementation for User Story 3

- [x] T014 [US3] Add `<link rel="stylesheet" href="{% static 'css/global_ux.css' %}">` to `extrahead` block in `templates/base.html`
- [x] T015 [US3] Verify `templates/unfold/layouts/base.html` does not cause infinite recursion in inheritance

**Checkpoint**: User Story 3 is functional - the application UI is fully restored.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and verification

- [x] T016 [P] Perform final automated scan for tag ordering using `grep -rn "{% extends" core/templates/ quiz/templates/ | grep -v ":1:"`
- [x] T017 [P] Run `python manage.py check` to ensure zero template syntax errors
- [x] T018 [P] Manually verify responsive UI elements are working as intended after CSS restoration

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: Core structural requirement. BLOCKS US2.
- **US2 (Phase 4)**: Depends on US1.
- **US3 (Phase 5)**: Depends on US2 (for `static` tag resolution).

### Parallel Opportunities

- T006 and T007 can run in parallel.
- T012 and T013 can run in parallel.
- Final polish tasks (T016, T017, T018) can run in parallel.

---

## Implementation Strategy

### MVP First (Structural Fix)

1. Complete Phase 3 (US1) to restore basic template inheritance.
2. Complete Phase 4 (US2) to ensure asset loading works.

### Final Delivery

1. Complete Phase 5 (US3) to restore the global look and feel.
2. Final validation.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each logical group of fixes
