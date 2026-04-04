# Tasks: Authentication Redirects Flow

**Input**: Design documents from `/specs/011-auth-redirects/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

There are no setup tasks required for this internal feature.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

There are no foundational prerequisites required as this feature utilizes the existing Django project setup.

---

## Phase 3: User Story 1 - Anonymous User Dashboard Access (Priority: P1) 🎯 MVP

**Goal**: As an anonymous unauthenticated user, I want to be redirected to the login page when I attempt to access the dashboard.

**Independent Test**: Can be fully tested by accessing `/dashboard/` in an incognito window and verifying the redirection to `/management/login/`.

### Implementation for User Story 1

- [x] T001 [US1] Update `supervisor_dashboard` view in `core/views.py` to use `@login_required(login_url='management_login')`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently by validating unauthenticated dashboard accesses.

---

## Phase 4: User Story 2 - Authenticated User Login Access (Priority: P1)

**Goal**: As a currently authenticated user, I want to be redirected directly to the dashboard if I mistakenly navigate to the login page.

**Independent Test**: Can be fully tested by logging in successfully, manually typing `/management/login/` in URL, and verifying redirection to `/dashboard/`.

### Implementation for User Story 2

- [x] T002 [US2] Update `management_login` view in `core/views.py` to check `request.user.is_authenticated` and execute `return redirect('supervisor_dashboard')` irrespective of role.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T003 Validate changes end-to-end following `/specs/011-auth-redirects/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A
- **Foundational (Phase 2)**: N/A
- **User Stories (Phase 3+)**: US1 and US2 can be executed sequentially or together.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies. Modifies `core/views.py`.
- **User Story 2 (P1)**: No dependencies. Modifies `core/views.py`.

### Within Each User Story

- Ensure logic maintains current behavior for paths not specified in requirements.
- Core implementation before integration.

### Parallel Opportunities

- Due to the nature of standard file locking and that both modify `core/views.py`, they should be done sequentially by the same entity unless concurrent editing on different lines is well handled.

---

## Parallel Example: User Story 1 & 2

N/A, tasks should be executed sequentially.

---

## Implementation Strategy

### MVP First (User Story 1 & 2 Together)

Given the minimal scope of this feature, US1 and US2 should be implemented simultaneously as a single MVP delivery.

1. Implement T001.
2. Implement T002.
3. Validate T003.

### Incremental Delivery

1. Implement US1 -> verify unauthenticated redirect logic.
2. Implement US2 -> verify authenticated redirect logic.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
