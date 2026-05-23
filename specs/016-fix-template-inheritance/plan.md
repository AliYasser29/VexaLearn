# Implementation Plan: Fix Template Inheritance and Missing CSS

**Branch**: `016-fix-template-inheritance` | **Date**: 2026-04-04 | **Spec**: [specs/016-fix-template-inheritance/spec.md](spec.md)
**Input**: Feature specification for fixing Django template inheritance and restoring global CSS.

## Summary
The plan involves scanning all HTML templates in `core/` and `quiz/` apps to ensure that the `{% extends %}` tag is the very first line in files that use it. Any `{% load static %}` tags will be moved to follow `{% extends %}`. Additionally, `templates/base.html` will be updated to correctly include the `global_ux.css` link to restore the UI globally.

## Technical Context

**Language/Version**: Python 3.12, Django 5.0
**Primary Dependencies**: `django-unfold`, `font-awesome`
**Storage**: N/A (UI layer fix)
**Testing**: manual verification + `python manage.py check`
**Target Platform**: Linux server
**Project Type**: web-service
**Performance Goals**: N/A
**Constraints**: Strict adherence to DTL tag ordering rules.
**Scale/Scope**: ~20 HTML templates across 2 apps.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Architecture**: Follows DTL best practices for inheritance.
- [x] **Data Integrity**: N/A (No model changes).
- [x] **Security**: N/A.
- [x] **Performance**: N/A.
- [x] **Code Quality**: Adheres to DRY by leveraging a global base template and consistent tag usage.

## Project Structure

### Documentation (this feature)

```text
specs/016-fix-template-inheritance/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Findings on tag ordering and CSS missing causes
├── data-model.md        # Conceptual template inheritance tree
└── quickstart.md        # Verification and troubleshooting guide
```

### Source Code (repository root)

```text
core/templates/core/
├── ...                  # Scanned and fixed templates

quiz/templates/quiz/
├── ...                  # Scanned and fixed templates

templates/
├── base.html            # Updated to include global_ux.css
└── unfold/layouts/
    └── base.html        # Verified for correct inheritance
```

**Structure Decision**: We will perform a surgical update of the existing template files. No new files or directories are required for this fix.

## Complexity Tracking

*No violations identified.*
