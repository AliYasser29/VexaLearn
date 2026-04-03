# Tasks: Platform Performance Optimization

**Feature**: Platform Performance Optimization  
**Plan**: [/specs/006-performance-optimization/plan.md](/specs/006-performance-optimization/plan.md)  
**Branch**: `006-performance-optimization`

## Phase 1: Setup

- [x] T001 Update `academy_project/settings.py` to add `WHITENOISE_MAX_AGE = 31536000` for static file caching
- [x] T002 Create a new file `core/middleware.py` with a basic structure for custom middleware

## Phase 2: Foundational

- [x] T003 Implement `MediaCacheMiddleware` in `core/middleware.py` to inject `Cache-Control` headers for `/media/` responses
- [x] T004 Add `core.middleware.MediaCacheMiddleware` to `MIDDLEWARE` in `academy_project/settings.py`

## Phase 3: User Story 1 - Fast Complex Data Retrieval (P1)

**Goal**: Eliminate N+1 queries in complex views to achieve < 1.5s load times.  
**Independent Test**: Load the supervisor dashboard and library pages while monitoring with Django Debug Toolbar to ensure query count is flat.

- [x] T005 [P] [US1] Update `active_enrollments` query in `core/views.py` (`supervisor_dashboard`) to use `.select_related('course')` and `.prefetch_related('attendances')`
- [x] T006 [P] [US1] Update `students` query in `core/views.py` (`supervisor_dashboard`) to properly use the optimized `Prefetch` object for enrollments
- [x] T007 [P] [US1] Override `get_queryset` in `EnrollmentAdmin` (`core/admin.py`) to use `.prefetch_related('attendances')` for the `attendance_summary` calculation
- [x] T008 [P] [US1] Update `CourseMaterial` queries (e.g., in library views) to use `.select_related('course', 'teacher')`

## Phase 4: User Story 2 - Rapid Media & Static Delivery (P2)

**Goal**: Ensure static and media files load instantly for returning users.  
**Independent Test**: Clear browser cache, reload a media-heavy page twice, and verify `304 Not Modified` or disk cache hits with the correct `Cache-Control` headers.

- [x] T009 [P] [US2] Verify WhiteNoise configuration correctly serves static files with `max-age` headers in development/production modes
- [x] T010 [P] [US2] Verify `MediaCacheMiddleware` successfully appends `Cache-Control` to responses originating from the `MEDIA_URL` path

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T011 Run `manage.py test` to ensure performance optimizations haven't broken any existing view logic
- [x] T012 Manually test the platform (Admin Panel, Supervisor Dashboard) to confirm visual stability and functionality remain intact

## Dependencies

- Phase 2 depends on Phase 1 (creating `middleware.py`).
- Phase 4 depends on Phase 2 (middleware implementation).
- Phase 3 tasks can be executed in parallel as they touch different parts of the querying logic.

## Implementation Strategy

1. **MVP (Phase 3)**: Tackle the N+1 queries first, as this provides the most immediate and noticeable improvement to server response times and database load.
2. **Incremental Delivery**: Follow up with static and media caching to improve client-side rendering speeds.
