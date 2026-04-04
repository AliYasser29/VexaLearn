# Tasks: Fix Super Monitor Error

**Input**: Design documents from `/specs/009-fix-super-monitor-error/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: No specific new tests were requested, but we will ensure existing tests pass after the fix.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Target file: `core/templates/core/universal_chat_monitor.html`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Navigate to project root and ensure virtual environment is active.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*No foundational tasks required as this is a simple template fix on an existing infrastructure.*

---

## Phase 3: User Story 1 - Administrator can access the universal chat monitor (Priority: P1) 🎯 MVP

**Goal**: Fix the `TemplateSyntaxError` at the `/super-monitor/` endpoint by correcting the syntax of conditional statements in the Django template.

**Independent Test**: Can be fully tested by accessing the `/super-monitor/` endpoint as an authorized administrator. The page should load properly without displaying a 500 server error.

### Implementation for User Story 1

- [x] T002 [US1] Locate `core/templates/core/universal_chat_monitor.html` and fix the `user1_id==u.id` comparison (approx line 352) by adding spaces around the `==` operator (`user1_id == u.id`).
- [x] T003 [US1] Locate `core/templates/core/universal_chat_monitor.html` and fix the `user2_id==u.id` comparison (approx line 366) by adding spaces around the `==` operator (`user2_id == u.id`).
- [x] T004 [US1] Run existing pytest suite (`pytest`) to ensure no regressions.
- [x] T005 [US1] Start the development server (`python manage.py runserver`) and manually verify the `/super-monitor/` page loads without a 500 error.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

*No additional polish tasks needed for this surgical fix.*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: N/A
- **User Stories (Phase 3+)**: Depends on Setup.

### User Story Dependencies

- **User Story 1 (P1)**: The only user story for this feature.

### Within Each User Story

- Template edits must be made before running tests and manual verification.

### Parallel Opportunities

- Due to the surgical nature of this fix targeting a single file, there are no significant parallel opportunities.

---

## Parallel Example: User Story 1

*(Not applicable due to single file scope)*

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 3: User Story 1 (Template fixes)
3. **STOP and VALIDATE**: Run tests and manually verify the endpoint.
4. Deploy/demo if ready

### Incremental Delivery

*(Not applicable as this is a single, atomic fix)*

### Parallel Team Strategy

*(Not applicable as this is a single, atomic fix)*
