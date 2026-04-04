# Implementation Plan: 011-auth-redirects

**Branch**: `011-auth-redirects` | **Date**: 2026-04-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-auth-redirects/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Enforce authentication on the `/dashboard/` view to redirect anonymous users to `/management/login/`, and update the `/management/login/` view to immediately redirect authenticated users to `/dashboard/`. This enhances user experience.

## Technical Context

**Language/Version**: Python 3.12, Django 5.0  
**Primary Dependencies**: Django (auth, views)  
**Storage**: SQLite 3 (existing)  
**Testing**: pytest  
**Target Platform**: Linux server  
**Project Type**: web-application  
**Performance Goals**: <200ms p95  
**Constraints**: Zero Plain-Text Secrets  
**Scale/Scope**: < 10 lines modified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Architecture**: Aligns with "Fat Models, Thin Views" and RBAC constraints. (Using standard Django view decorators and redirect flows).
- [x] **Data Integrity**: Uses Soft Delete pattern for all critical entities. (No deletions involved).
- [x] **Security**: Addresses Zero Plain-Text Secrets and Strict Token Expirations. (No tokens or secrets involved).
- [x] **Performance**: Mitigates N+1 queries. Background tasks planned for async jobs. (No new DB queries added).
- [x] **Code Quality**: Utilizes proper Formsets and adheres to DRY principle (e.g. abstract base models). (Reusing existing `@login_required` decorators).

## Project Structure

### Documentation (this feature)

```text
specs/011-auth-redirects/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
└── tasks.md             
```

### Source Code (repository root)

```text
core/
└── views.py
```

**Structure Decision**: Modified the existing `core/views.py` file to adjust the authentication checks and redirection paths. No structural project changes needed.
