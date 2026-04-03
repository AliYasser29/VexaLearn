# Tasks: Excel Data Export

**Feature**: Excel Data Export  
**Plan**: [/specs/008-excel-data-export/plan.md](/specs/008-excel-data-export/plan.md)  
**Branch**: `008-excel-data-export`

## Phase 1: Setup

- [x] T001 Install `django-import-export` and `openpyxl` in the environment
- [x] T002 Add `django-import-export` and `openpyxl` to `requirements.txt`
- [x] T003 Add `import_export` to `INSTALLED_APPS` in `academy_project/settings.py`

## Phase 2: Foundational

- [x] T004 Create `core/resources.py` and set up the base imports from `import_export` and `core.models`

## Phase 3: User Story 1 - Export User Records (P1)

**Goal**: Enable authorized admins to export Student and Teacher records as well-formatted Excel files.  
**Independent Test**: Log in as superuser. Go to Students and Teachers admin views. Export the lists and verify columns contain human-readable names instead of IDs.

- [x] T005 [P] [US1] Define `StudentResource` in `core/resources.py` with specific fields and `dehydrate` methods for `country`, `education_type`, and `academic_year`
- [x] T006 [P] [US1] Define `TeacherResource` in `core/resources.py` with specific fields and a `dehydrate` method for the `subjects` M2M field
- [x] T007 [P] [US1] Update `StudentAdmin` in `core/admin.py` to inherit from `unfold.contrib.import_export.ModelAdmin` and `ImportExportModelAdmin` and link `StudentResource`
- [x] T008 [P] [US1] Update `TeacherAdmin` in `core/admin.py` to inherit from `unfold.contrib.import_export.ModelAdmin` and `ImportExportModelAdmin` and link `TeacherResource`

## Phase 4: User Story 2 - Export Operational Data (P1)

**Goal**: Enable authorized admins to export filtered Enrollment and Attendance records as Excel files.  
**Independent Test**: Log in as superuser. Go to Attendances and Enrollments. Apply a filter, export the list, and verify the downloaded file respects the filter and contains human-readable names.

- [x] T009 [P] [US2] Define `EnrollmentResource` in `core/resources.py` with `dehydrate` methods for `student`, `course`, and `teacher`
- [x] T010 [P] [US2] Define `AttendanceResource` in `core/resources.py` with `dehydrate` methods for `status` and traverse relationships for `student_name` and `course_name`
- [x] T011 [P] [US2] Update `EnrollmentAdmin` in `core/admin.py` to inherit from `unfold.contrib.import_export.ModelAdmin` and `ImportExportModelAdmin` and link `EnrollmentResource`
- [x] T012 [P] [US2] Update `AttendanceAdmin` in `core/admin.py` to inherit from `unfold.contrib.import_export.ModelAdmin` and `ImportExportModelAdmin` and link `AttendanceResource`

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T013 Verify export functionality works correctly with `.xlsx` format specifically
- [x] T014 Verify that non-superuser/non-manager roles (e.g., standard Teachers) do not have access to the export actions in the admin UI

## Dependencies

- Phase 2 depends on Phase 1.
- Phase 3 and Phase 4 depend on Phase 2 (`core/resources.py` creation).
- Tasks within Phase 3 and Phase 4 can be executed in parallel where marked `[P]`, provided the resource is defined before linking it in the admin.

## Implementation Strategy

1. **MVP**: Implement User Story 1 (Students & Teachers) to establish the pattern for `ModelResource` definition and Unfold integration.
2. **Incremental Delivery**: Apply the established pattern to the operational data (Enrollments & Attendances) in User Story 2.
