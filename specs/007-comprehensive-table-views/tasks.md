# Tasks: Comprehensive Table Views

**Feature**: Comprehensive Table Views  
**Plan**: [/specs/007-comprehensive-table-views/plan.md](/specs/007-comprehensive-table-views/plan.md)  
**Branch**: `007-comprehensive-table-views`

## Phase 1: Setup

- [x] T001 Install `django-filter` in the environment
- [x] T002 Add `django-filter` to `requirements.txt`
- [x] T003 Add `django_filters` to `INSTALLED_APPS` in `academy_project/settings.py`

## Phase 2: Foundational

- [x] T004 [P] Update `StudentAdmin` in `core/admin.py` to ensure `search_fields` and `list_per_page` are properly configured
- [x] T005 [P] Update `TeacherAdmin` in `core/admin.py` to ensure `search_fields` and `list_per_page` are properly configured

## Phase 3: User Story 1 & 2 - Student Grid View & Filtering (P1)

**Goal**: Provide a unified, filterable grid for Students.  
**Independent Test**: Navigate to the Students page in the Admin UI. Verify the "Active Courses" column displays correct data without N+1 queries. Apply filters (e.g., Country + Academic Year) and ensure correct pagination.

- [x] T006 [US1] Create `get_active_enrollments` method in `StudentAdmin` (`core/admin.py`) to return a formatted string of active courses for a student
- [x] T007 [US1] Add `get_active_enrollments` to `list_display` in `StudentAdmin`
- [x] T008 [US1] Override `get_queryset` in `StudentAdmin` to `prefetch_related` on enrollments to optimize the `get_active_enrollments` method
- [x] T009 [US2] Configure robust `list_filter` combinations in `StudentAdmin` (e.g., `country`, `education_type`, `academic_year`, `supervisor`)

## Phase 4: User Story 3 - Teacher Grid View (P2)

**Goal**: Provide a unified, filterable grid for Teachers showing subjects and workload.  
**Independent Test**: Navigate to the Teachers page in the Admin UI. Verify "Subjects" and "Active Students" columns display correctly. Filter by subject.

- [x] T010 [US3] Create `get_student_count` method in `TeacherAdmin` (`core/admin.py`) to calculate the number of active enrollments tied to the teacher
- [x] T011 [US3] Update `list_display` in `TeacherAdmin` to include `get_subjects` (existing) and the new `get_student_count`
- [x] T012 [US3] Override `get_queryset` in `TeacherAdmin` to `prefetch_related` subjects and enrollments to prevent N+1 queries for the new columns
- [x] T013 [US3] Configure `list_filter` in `TeacherAdmin` to allow filtering by `subjects`

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T014 Run a visual check on the Unfold admin interface to ensure the new columns format correctly without text overflow issues
- [x] T015 Verify query counts using Django Debug Toolbar on both Student and Teacher list views to ensure SC-001 (performance) is met


## Dependencies

- Phase 2 depends on Phase 1.
- Phase 3 and Phase 4 can be worked on in parallel after Phase 2 is complete.

## Implementation Strategy

1. **MVP (Phase 3)**: Implement the complex Student Grid first, as it aggregates the most critical operational data and serves as a template for how `list_display` methods and prefetching should work together within Unfold.
2. **Incremental Delivery**: Replicate the pattern for the Teacher grid (Phase 4).
