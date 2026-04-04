# Implementation Plan: 012-ui-ux-overhaul

**Branch**: `012-ui-ux-overhaul` | **Date**: 2026-04-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-ui-ux-overhaul/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

A massively detailed, platform-wide UI/UX overhaul across 5 pillars (Django Unfold admin styling, Public Auth pages, Role-Based Dashboards, Communication Hub, and Global Micro-interactions). We will consolidate global styles, implement ARIA attributes, and refine modern layouts.

## Technical Context

**Language/Version**: Python 3.12, Django 5.0, HTML5, Vanilla CSS / JS  
**Primary Dependencies**: Django Templates, Django Unfold  
**Storage**: N/A (UI layer only)  
**Testing**: UI/UX Manual Validation across breakpoints  
**Target Platform**: Web (Mobile-First responsive)  
**Project Type**: web-application  
**Performance Goals**: >85 Mobile PageSpeed, >90 Accessibility  
**Constraints**: Do not introduce heavy frontend frameworks (React/Vue/Angular). Use existing stack.  
**Scale/Scope**: >10 HTML templates modified, new CSS asset creation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Architecture**: Retaining 'Thin Views' by injecting CSS/design into templates directly.
- [x] **Data Integrity**: Does not compromise Soft Deletes.
- [x] **Security**: UI/UX changes preserve Token Expirations and Zero Plain-Text Secrets.
- [x] **Performance**: Avoids external heavy CSS/JS downloads ensuring fast loading times. Skeletal loaders improve perceived performance.
- [x] **Code Quality**: Global CSS keeps code DRY instead of inline styles.

## Project Structure

### Documentation (this feature)

```text
specs/012-ui-ux-overhaul/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
└── tasks.md             
```

### Source Code (repository root)

```text
academy_project/
└── settings.py
core/
├── static/css/
│   └── global_ux.css 
└── templates/core/
    ├── landing_page.html
    ├── public_login.html
    ├── management_login.html
    ├── superuser_login.html
    ├── profile.html
    ├── supervisor_dashboard.html
    ├── course_materials.html
    ├── chat.html
    ├── video_call.html
    └── universal_chat_monitor.html
```

**Structure Decision**: Added new consolidated CSS file and explicitly declared layout refactoring mapping for existing UI templates under `core/templates/core`.
