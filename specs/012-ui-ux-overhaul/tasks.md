# Tasks: UI UX Overhaul

**Input**: Design documents from `/specs/012-ui-ux-overhaul/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

There are no setup tasks required for this UI redesign as it hooks into the existing framework.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T001 Initialize global variable CSS file `core/static/css/global_ux.css` containing baseline variables and toast/skeleton frameworks.
- [ ] T002 Link `core/static/css/global_ux.css` inside overarching HTML headers where applicable (or rely on base layout if implemented during US updates).

**Checkpoint**: Base styles are in place ensuring the following templates scale accurately.

---

## Phase 3: User Story 1 - Admin Panel Streamlining (Priority: P1) 🎯 MVP

**Goal**: Optimize Django Unfold admin interface configuration for structural improvements.

**Independent Test**: Can be independently verified by logging in as an admin and navigating the sidebar.

### Implementation for User Story 1

- [ ] T003 [US1] Update Unfold configurations, themes, and colors inside `academy_project/settings.py`.

**Checkpoint**: Admin panel renders with enhanced Django Unfold customization.

---

## Phase 4: User Story 2 - Public & Auth Page Redesign (Priority: P1)

**Goal**: Revamp the landing page and authentication views with responsive layouts and visual form validation states.

**Independent Test**: Load landing page and login screens from mobile and desktop views to verify responsiveness and form validations.

### Implementation for User Story 2

- [ ] T004 [P] [US2] Update `core/templates/core/landing_page.html` referencing global_ux.css for responsive styling.
- [ ] T005 [P] [US2] Redesign `core/templates/core/public_login.html` applying form validation visual feedback.
- [ ] T006 [P] [US2] Redesign `core/templates/core/management_login.html` matching standard auth UX styling.
- [ ] T007 [P] [US2] Redesign `core/templates/core/superuser_login.html` aligning with universal auth layouts.

**Checkpoint**: All auth and landing pages display beautifully on mobile and validate inputs immediately via CSS pseudo-classes.

---

## Phase 5: User Story 3 - Role-Based Dashboard Modernization (Priority: P2)

**Goal**: Replace native dashboard lists with card layouts, including empty-state graphics.

**Independent Test**: Access dashboard views under active and empty states.

### Implementation for User Story 3

- [ ] T008 [P] [US3] Refactor `core/templates/core/profile.html` applying card-based layout and empty-state placeholders.
- [ ] T009 [P] [US3] Refactor `core/templates/core/supervisor_dashboard.html` adding clean container layouts for data readability.
- [ ] T010 [P] [US3] Upgrade `core/templates/core/course_materials.html` injecting file-type iconography bounds.

**Checkpoint**: User specific dashboards utilize structured CSS grids/flexboxes correctly.

---

## Phase 6: User Story 4 - Communication Hub Revamp (Priority: P2)

**Goal**: Convert basic chat outputs to responsive bubble systems and establish scaled video grids.

**Independent Test**: Navigate to chat and video feeds verifying adaptive DOM scaling and visual contrast.

### Implementation for User Story 4

- [ ] T011 [P] [US4] Modify `core/templates/core/chat.html` introducing sender/receiver color contrast bubbles.
- [ ] T012 [P] [US4] Modify `core/templates/core/universal_chat_monitor.html` standardizing observation layouts mirroring `chat.html`.
- [ ] T013 [P] [US4] Update `core/templates/core/video_call.html` restructuring the UI to handle dynamic grid sizes natively.

**Checkpoint**: The communication channels replicate messaging-platform clarity patterns.

---

## Phase 7: User Story 5 - Global UX & Micro-interactions (Priority: P3)

**Goal**: Enforce application-wide UX rules spanning dynamic loading, toasts, and accessibility standards.

**Independent Test**: Evaluate the triggers for slow connections and button hover accessibility.

### Implementation for User Story 5

- [ ] T014 [P] [US5] Inject ARIA attributes and skeletal logic triggers across templates modified during previous phases.
- [ ] T015 [P] [US5] Finalize Global UX JS/CSS dependencies referencing skeleton loaders inside asynchronous triggers (if any).

**Checkpoint**: Complete platform polish achieved.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T016 Run manual validation across breakpoints utilizing `quickstart.md` procedures.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A
- **Foundational (Phase 2)**: Mandatory starting point to bind CSS properties prior to template replacements.
- **User Stories**: US1 and US2 can run independently or in parallel. US3, US4, US5 sequentially follow since they branch from foundational layers.
- **Polish (Final Phase)**: Runs at the end.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies. Modifies `academy_project/settings.py`.
- **User Story 2 (P1)**: Depends on Foundational. Modifies isolated auth components.
- **User Story 3 (P2)**: Depends on Foundational.
- **User Story 4 (P2)**: Depends on Foundational.
- **User Story 5 (P3)**: Relies on completed DOM layouts across all preceding phases.

### Within Each User Story

- Parallel processing operates smoothly per User Story block since each task modifies separate `.html` files natively mapped [P].

### Parallel Opportunities

- HTML template adjustments can be done thoroughly in parallel.
- US2 tasks (T004 - T007) are exclusively standalone files.
- US3 tasks (T008 - T010) are exclusively standalone files.
- US4 tasks (T011 - T013) are exclusively standalone files.

---

## Parallel Example: User Story 2

```bash
# Launch layout refactors in parallel
Task: "Redesign public_login.html applying form validation..."
Task: "Redesign management_login.html matching standard auth UX styling."
```

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Establish Foundational CSS variables.
2. Complete US1 to align the robust Admin interface.
3. Complete US2 fixing basic authentication flows.
4. Stop and demo core entrance views.

### Incremental Delivery

1. Implement US3 (Dashboards).
2. Implement US4 (Communication hubs).
3. Conclude with US5 applying deep DOM ARIA/skeletal logic platform-wide.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Wait incrementally as each interface undergoes heavy architectural rewrites
