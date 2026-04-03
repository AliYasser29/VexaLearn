---
description: "Task list for Chat Performance Optimization and Video Call Security implementation"
---

# Tasks: Chat Performance Optimization and Video Call Security

**Input**: Design documents from `/specs/003-chat-perf-video-security/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths are included in the descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project readiness and structural checks

- [x] T001 Verify `core/views.py` target endpoints (`chat_room` and `video_call_view`) exist and are ready for refactoring.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must be present before views can tie the elements together.

- [x] T002 [P] Import `Q` object from `django.db.models` enabling explicit optimized ORM combinations inside `core/views.py`.

**Checkpoint**: Foundation ready - necessary dependencies configured via Django logic bounds ready for routing integration.

---

## Phase 3: User Story 1 - Optimized Chat Contact Loading (Priority: P1) 🎯 MVP

**Goal**: When a user accesses the chat interface, the system must immediately load their list of available contacts without causing system-wide database locking or severe latency delays.

**Independent Test**: Load the chat interface as an actively enrolled student and as a highly connected teacher. Verify that the contact list populates instantaneously without duplicated names and logs single SQL executions.

### Implementation for User Story 1

- [x] T003 [US1] Remove legacy explicit loop patterns and raw `|` QuerySet iterations from `chat_room` building `users_list` arrays manually within `core/views.py`.
- [x] T004 [US1] Implement native SQL execution via `User.objects.filter(Q(...) | Q(...)).exclude(id=request.user.id).distinct()` mapping overlaps directly bridging relationship scopes within `core/views.py`.

**Checkpoint**: At this point, User Story 1 is fully functional. Teachers and students can load thousands of contacts cleanly over the wire leveraging native database computation.

---

## Phase 4: User Story 2 - Secure Video Call Authentication (Priority: P1)

**Goal**: To prevent unauthorized broadcasting interactions, users attempting to access live video rooms must be actively confirmed as participating members and hold tokens that expire concisely after 2 hours.

**Independent Test**: Attempt to access a video token as a user unassociated with a course instance. Verify the gateway blocks access. Verify authorized streams time out immediately after expected limits.

### Implementation for User Story 2

- [x] T005 [P] [US2] Update `expiration_time_in_seconds` variable scaling directly from `86400` down to `7200` seconds protecting standard `RtcTokenBuilder` calls within `core/views.py`.
- [x] T006 [US2] Inject pre-authorization database guard conditionally verifying `Course.objects.filter(id=..., teacher=request.user)` or `Enrollment.objects.filter(course_id=..., student=...)` blocking execution prior to payload hashing within `core/views.py`.

**Checkpoint**: At this point, User Stories 1 AND 2 safely coexist preventing lagging data structures and locking out video footprint attacks across the backend routes.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that wrap up the implementation features tracking final behaviors.

- [x] T007 Run local `quickstart.md` testing verifying 0 duplication instances natively bridging views routing.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Trivial syntax implementations unlocking route modifications.
- **User Story 1 (P1)**: Fully refactors python iterables towards `Q` object filters.
- **User Story 2 (P1)**: Fully refactors python payload logic modifying variables isolated outside of US1 logic.
- **Polish (Final Phase)**: Runs locally tracking test data mappings.

### Parallel Opportunities

```bash
# Since the features affect distinct Python routes (`chat_room` vs `video_call`), US1 and US2 can execute simultaneously.
Developer A: Phase 3 logic optimizing queries (T003, T004) -> core/views.py
Developer B: Phase 4 logic altering Agora params (T005, T006) -> core/views.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2: Setup Database Dependency logic (`Q` imports).
2. Execute Phase 3 isolating chat load bounds and deploy directly tracking server performance gains.
3. **STOP and VALIDATE**: Test backend latency improvements verifying query loads via Django Toolbar.

### Incremental Delivery

1. Drop lag latency directly via `chat_room` refactor. Deploy.
2. Secure application footprint narrowing video bounds via `video_call_view` guard rails reducing total exploitation window scopes. Deploy.
