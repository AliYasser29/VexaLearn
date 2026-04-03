# Implementation Plan: [FEATURE]

**Branch**: `001-safe-student-registration` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-safe-student-registration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement an abstract `SoftDeleteModel` with a boolean `is_deleted` field and custom manager to safely deactivate user accounts (Teachers, Students, Supervisors, Managers) without breaking historical records. Additionally, update the `admin_panel` view to explicitly display generated credentials via `django.contrib.messages.success` immediately following student creation to provide an admin fallback if email delivery fails.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Django >= 5.0, django-unfold
**Storage**: Django ORM (SQLite/PostgreSQL)
**Testing**: Django TestCase
**Target Platform**: Web Server
**Project Type**: Web Application
**Performance Goals**: Avoid N+1 issues when fetching user listings; instantaneous soft deletes (<100ms).
**Constraints**: Must strictly adhere to Django "Fat Models, Thin Views" and never physically `DELETE` from critical entity tables.
**Scale/Scope**: Administrative module for Academy platform

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **Architecture**: Aligns with "Fat Models, Thin Views" and RBAC constraints.
- [ ] **Data Integrity**: Uses Soft Delete pattern for all critical entities.
- [ ] **Security**: Addresses Zero Plain-Text Secrets and Strict Token Expirations.
- [ ] **Performance**: Mitigates N+1 queries. Background tasks planned for async jobs.
- [ ] **Code Quality**: Utilizes proper Formsets and adheres to DRY principle (e.g. abstract base models).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
core/
├── models.py       # SoftDeleteModel and user models implementation
├── views.py        # admin_panel views and messages updates
└── admin.py        # Admin panel integration and queryset tweaks

tests/
└── test_users.py   # Test cases for Soft Delete functionality and view messages
```

**Structure Decision**: Standard Django App structure using the `core` app, keeping `SoftDeleteModel` within `core/models.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
