# Implementation Plan: Excel Data Export

**Branch**: `008-excel-data-export` | **Date**: April 3, 2026 | **Spec**: [/specs/008-excel-data-export/spec.md](/specs/008-excel-data-export/spec.md)
**Input**: Feature specification from `/specs/008-excel-data-export/spec.md`

## Summary
Implement data export to Excel (.xlsx) for Students, Teachers, Enrollments, and Attendances using `django-import-export` integrated with the `django-unfold` theme. Custom `ModelResource` classes will be created to ensure foreign keys and choices are translated into human-readable strings.

## Technical Context

**Language/Version**: Python 3.12, Django 5.0
**Primary Dependencies**: `django-import-export`, `django-unfold`, `openpyxl` (for xlsx support)
**Storage**: SQLite 3 (existing)
**Testing**: Django test runner
**Target Platform**: Linux/Web
**Project Type**: Web Application (Django)
**Performance Goals**: Export up to 10,000 records in under 10 seconds synchronously.
**Constraints**: RBAC (Superuser/Manager only), respect active admin filters.
**Scale/Scope**: Admin interface enhancements for 4 core entities.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Architecture**: Aligns with "Fat Models, Thin Views". Export logic encapsulates nicely in Resource classes.
- [x] **Data Integrity**: Read-only operation; does not affect data integrity or soft delete patterns.
- [x] **Security**: RBAC is maintained via Django Admin permissions (`has_export_permission`).
- [x] **Performance**: Uses standard querysets which will leverage the existing `select_related` / `prefetch_related` optimizations in `core/admin.py` to prevent N+1 queries during serialization.
- [x] **Code Quality**: Adheres to DRY principle by creating reusable export resources.

## Project Structure

### Documentation (this feature)

```text
specs/008-excel-data-export/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
├── checklists/
│   └── requirements.md  
└── tasks.md             
```

### Source Code (repository root)

```text
core/
├── admin.py             # Add ExportActionModelAdmin / Unfold mixins to ModelAdmins
├── resources.py         # NEW: Define ModelResource classes for export formatting
academy_project/
├── settings.py          # Add import_export to INSTALLED_APPS
requirements.txt         # Add django-import-export, openpyxl
```

**Structure Decision**: Standard Django App structure modifications. A new `resources.py` file will be created in the `core` app to house the `django-import-export` definitions, keeping `admin.py` clean.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
