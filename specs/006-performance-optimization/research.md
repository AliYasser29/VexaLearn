# Research: Performance Optimization

## Decision 1: Resolving N+1 Queries
**Decision**: Apply strict `select_related` and `prefetch_related` in `core/views.py` and `core/admin.py`.
**Rationale**: 
- In `core/views.py` (`supervisor_dashboard`), the `active_enrollments` queryset is prefetched but lacks `.select_related('course')` and `.prefetch_related('attendances')`, causing N+1 queries in the template when accessing `enrollment.course.name` and `enrollment.attendances.count()`.
- In `core/admin.py`, `EnrollmentAdmin.attendance_summary` causes N+1 queries. We will override `get_queryset` to prefetch `attendances`.
**Alternatives considered**: Using `django-auto-prefetch`, but explicit prefetching is more predictable and better for complex queries.

## Decision 2: Static File Caching
**Decision**: Enhance existing WhiteNoise configuration.
**Rationale**: WhiteNoise is already installed. Setting `WHITENOISE_MAX_AGE = 31536000` (1 year) will ensure browsers cache static assets aggressively.
**Alternatives considered**: CDN offloading for static files, but WhiteNoise is simpler and sufficient for the current stack.

## Decision 3: Media File Caching
**Decision**: Implement a custom middleware to inject `Cache-Control` headers for `/media/` routes.
**Rationale**: WhiteNoise does not serve media files in production securely by default. Providing a fallback Django middleware for caching media ensures the FCP requirement is met even without complex Nginx configurations.
**Alternatives considered**: Using AWS S3/CloudFront. Rejected as it introduces infrastructure complexity not requested in the spec.
