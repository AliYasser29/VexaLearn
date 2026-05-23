# Implementation Plan: Dynamic Role-Based Navigation System

**Branch**: `015-dynamic-role-nav` | **Date**: 2026-04-04 | **Spec**: [specs/015-dynamic-role-nav/spec.md](spec.md)
**Input**: Feature specification for a global Dynamic Role-Based Navigation System.

## Summary
Implement a global context processor that injects role-specific navigation items (`nav_items`) into all templates. Create a unified `base.html` that integrates `django-unfold` styling and dynamically renders the navigation sidebar/navbar based on the user's role (Student, Teacher, Supervisor, or Manager).

## Technical Context

**Language/Version**: Python 3.12, Django 5.0
**Primary Dependencies**: `django-unfold`, `font-awesome`
**Storage**: SQLite 3 (Existing)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: web-service
**Performance Goals**: N/A (Standard UI navigation)
**Constraints**: Must follow `django-unfold` and Cairo font style.
**Scale/Scope**: 4 primary user roles, ~15 navigation items total.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Architecture**: Aligns with "Fat Models, Thin Views" by moving navigation logic to a context processor.
- [x] **Data Integrity**: N/A (No deletions involved).
- [x] **Security**: RBAC is core to this feature; views remain protected by decorators.
- [x] **Performance**: Navigation logic is lightweight; avoids complex database queries.
- [x] **Code Quality**: Adheres to DRY by centralizing navigation in a global `base.html`.

## Project Structure

### Documentation (this feature)

```text
specs/015-dynamic-role-nav/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Role mapping and design decisions
├── data-model.md        # NavItem schema
├── quickstart.md        # Setup and testing guide
└── checklists/          # Quality validation
```

### Source Code (repository root)

```text
core/
├── context_processors.py  # Inject nav_items logic
├── templatetags/          # nav_tags for active state highlighting
│   └── nav_tags.py
└── templates/
    └── base.html          # Global base template extending unfold

templates/
└── base.html              # Project-level base template (if preferred)
```

**Structure Decision**: A new `templates/base.html` will be created at the project root to serve as the global base. `core/context_processors.py` will be updated with `nav_items` logic.

## Complexity Tracking

*No violations identified.*
