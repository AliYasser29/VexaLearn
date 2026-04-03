# Tasks: Audit Log System

**Feature**: Audit Log System  
**Plan**: [/specs/005-audit-log-system/plan.md](/specs/005-audit-log-system/plan.md)  
**Branch**: `005-audit-log-system`

## Phase 1: Setup

- [x] T001 Install `django-simple-history` in the environment
- [x] T002 Add `django-simple-history` to `requirements.txt`
- [x] T003 [P] Add `simple_history` to `INSTALLED_APPS` in `academy_project/settings.py`
- [x] T004 [P] Add `simple_history.middleware.HistoryRequestMiddleware` to `MIDDLEWARE` in `academy_project/settings.py`

## Phase 2: Foundational

- [x] T005 [P] Add `HistoricalRecords(inherit=True)` to `SoftDeleteModel` in `core/models.py`
- [x] T006 [P] Add `HistoricalRecords()` to `Country`, `EducationType`, `AcademicYear`, and `Subject` in `core/models.py`
- [x] T007 [P] Add `HistoricalRecords()` to `Quiz`, `Question`, `Choice`, and `QuizAttempt` in `quiz/models.py`
- [x] T008 Generate and apply database migrations using `python manage.py makemigrations` and `python manage.py migrate`

## Phase 3: User Story 1 - Track Database Changes (P1)

**Goal**: Enable superusers to view history of modifications for all tracked models.  
**Independent Test**: Perform a change (create/update/soft-delete) on a model and verify the "History" button in Unfold displays the correct log entry.

- [x] T009 [P] [US1] Update `core/admin.py` to use `SimpleHistoryAdmin` mixin for all tracked models
- [x] T010 [P] [US1] Update `quiz/admin.py` to use `SimpleHistoryAdmin` mixin for all tracked models
- [x] T011 [US1] Verify per-object history view is accessible and functional in the Django Unfold dashboard

## Phase 2: User Story 2 - Investigate Specific Changes (P2)

**Goal**: Provide a global searchable/filterable audit log for superusers.  
**Independent Test**: Access the global "Audit Log" section and filter logs by user and date range.

- [x] T012 [US2] Register `HistoricalStudent` (or a generic History model) in `core/admin.py` to provide a global view
- [x] T013 [US2] Configure `django-unfold` sidebar in `academy_project/settings.py` or `core/dashboard.py` to include the Audit Log section
- [x] T014 [US2] Implement custom filters in the global history admin view for effective investigation

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T015 Verify that history tracking respects Superuser-only access (RBAC)
- [x] T016 Perform a basic performance check on log retrieval with multiple entries
- [x] T017 [P] Ensure all tracked models have appropriate verbose names for clear history logging

## Dependencies

- Phase 2 depends on Phase 1 (Installation).
- Phase 3 depends on Phase 2 (Data Model changes).
- Phase 4 depends on Phase 3 (Basic history functionality).

## Implementation Strategy

1. **MVP (User Story 1)**: Focus on model-level tracking and the per-object history view in the admin. This provides immediate value for auditing.
2. **Incremental Delivery**: Once individual logs are working, build the global aggregation view (User Story 2) for cross-platform monitoring.
3. **Parallelism**: Setup tasks (Phase 1) and adding `HistoricalRecords` to different apps (Phase 2) can be done in parallel.
