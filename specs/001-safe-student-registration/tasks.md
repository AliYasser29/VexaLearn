---
description: "Task list for Data Integrity and Safe Student Registration"
---

# Tasks: Data Integrity and Safe Student Registration

**Input**: Design documents from `/specs/001-safe-student-registration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths are included in the descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project readiness and structural checks

- [x] T001 [P] Verify `core` app and `tests` directories exist for implementations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must be present before the user deletions can be implemented properly.

- [x] T002 Create abstract `SoftDeleteModel` base class with `is_deleted` field in `core/models.py`
- [x] T003 Implement custom manager for `SoftDeleteModel` filtering `is_deleted=False` in `core/models.py`

**Checkpoint**: Foundation ready - UI updates and Database schema connections can proceed.

---

## Phase 3: User Story 1 - Secure Admin Registration Backup (Priority: P1) 🎯 MVP

**Goal**: Ensure administrators instantly see generated login credentials for new students to act as a fallback against email delivery failures.

**Independent Test**: Successfully register a dummy student in the admin panel and observe the newly generated plaintext credentials injected into the flash success message.

### Implementation for User Story 1

- [x] T004 [US1] Intercept generated plaintext password before context release in `core/views.py`
- [x] T005 [US1] Inject credentials into UI using `django.contrib.messages.success` in `core/views.py`

**Checkpoint**: At this point, User Story 1 is fully functional. Administrators will receive instant feedback containing backup credentials.

---

## Phase 4: User Story 2 - Safe Account Deletion and History Preservation (Priority: P2)

**Goal**: Prevent actual row deletions during admin deletion requests, instead flagging records and disabling login properties, retaining all interconnecting historical records.

**Independent Test**: Deleting an active user marks them as inactive, removes their login capabilities immediately, yet allows the user to persist in the Django shell via `.all_objects`.

### Implementation for User Story 2

- [x] T006 [P] [US2] Update `Teacher` model to inherit from `SoftDeleteModel` in `core/models.py`
- [x] T007 [P] [US2] Update `Student` model to inherit from `SoftDeleteModel` in `core/models.py`
- [x] T008 [P] [US2] Update `Supervisor` model to inherit from `SoftDeleteModel` in `core/models.py`
- [x] T009 [P] [US2] Update `Manager` model to inherit from `SoftDeleteModel` in `core/models.py`
- [x] T010 [US2] Override `delete()` method for all profile models to trigger `is_deleted = True` and `self.user.is_active = False` in `core/models.py`
- [x] T011 [US2] Execute `makemigrations` and `migrate` for changes in `core/models.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Data models are no longer forcefully dropped.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that wrap up the implementation features.

- [x] T012 [P] Implement backend tests for messages UI and soft delete behavior in `tests/test_users.py`
- [x] T013 Verify Constitution RBAC alignment for `admin_panel` in `core/views.py`
- [x] T014 Run quickstart.md validation locally

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Core abstract logic.
- **User Story 1 (P1)**: Does not heavily depend on the foundational data shapes. Can be implemented synchronously or in parallel with Phase 2/4.
- **User Story 2 (P2)**: Strongly bound to Foundational (Phase 2).
- **Polish (Final Phase)**: Depends on all user stories completed.

### Parallel Opportunities

```bash
# Update multiple database files concurrently for US2 once Foundation finishes:
Task T006, T007, T008, T009 can be scripted or updated side-by-side.

# Develop UI Messages alongside schema:
Developer 1: Phase 3 (US1 - core/views.py messages)
Developer 2: Phase 2 -> Phase 4 (US2 - core/models.py soft deletion wrapper)
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Bypass Phase 2 to directly target Phase 3 (US1 logic only alters views, isolated logic).
3. **STOP and VALIDATE**: Test User Story 1 independently via web server UI.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Complete US1 → Deploy admin messages fallback (MVP Delivery).
3. Complete US2 → Add `SoftDeleteModel` layer and execute schema migrations.
4. Each story independently adds massive value to data preservation workflows.
