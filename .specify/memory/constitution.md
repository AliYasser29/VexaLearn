<!--
SYNC IMPACT REPORT
Version change: [CONSTITUTION_VERSION] -> 1.0.0
Modified principles:
  - [PRINCIPLE_1_NAME] -> I. ARCHITECTURE & PATTERNS
  - [PRINCIPLE_2_NAME] -> II. DATA INTEGRITY
  - [PRINCIPLE_3_NAME] -> III. SECURITY RULES
  - [PRINCIPLE_4_NAME] -> IV. PERFORMANCE & SCALABILITY
  - [PRINCIPLE_5_NAME] -> V. CODE QUALITY & UI
Removed sections:
  - [SECTION_3_NAME]
Added sections:
  - None
Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Missing original adoption date.
  - TODO(ADDITIONAL_CONSTRAINTS): Optional extra constraints not defined yet.
-->
# VexaLearn Constitution

## Core Principles

### I. ARCHITECTURE & PATTERNS
- **Fat Models, Thin Views**: Follow strict Django "Fat Models, Thin Views" principles. Keep business logic out of templates and views where possible.
- **Role-Based Access Control (RBAC)**: Adhere strictly to the established Role-Based Access Control. Always verify user permissions (Superuser, Manager, Supervisor, Teacher, Student) before allowing actions.

### II. DATA INTEGRITY
- **No Physical Deletions**: Never use physical deletions (Hard Delete) for critical entities (Users, Teachers, Students, Courses, Enrollments).
- **Soft Delete Pattern**: Always implement a "Soft Delete" pattern (e.g., `is_deleted` or `is_active` flags) and override the model's `delete()` method to prevent breaking relationships and historical data like Chat Logs or Course Materials.

### III. SECURITY RULES
- **Zero Plain-Text Secrets**: Never rely solely on email for delivering generated passwords without a secure UI fallback for the admin.
- **Strict Token Expirations**: Third-party tokens (like Agora SDK) must have the absolute minimum required lifespan (e.g., 2 hours max, never 24 hours).
- **Access Control**: Always validate that the `request.user` is explicitly linked (via Enrollment or RBAC) to the resource they are trying to access (e.g., Video Rooms, Course Materials).

### IV. PERFORMANCE & SCALABILITY
- **Database Optimization**: Strictly avoid N+1 query problems. Always use `select_related` and `prefetch_related`. Avoid excessive QuerySet `.union()` operations; use optimized `Q` objects and annotations instead.
- **Asynchronous Operations**: Do not use standard Python threading for emails or heavy tasks within request/response cycles. Plan for robust background task queues (e.g., Celery/Redis).

### V. CODE QUALITY & UI
- **Dynamic Forms**: Avoid hardcoded HTML inputs for relational data. Always use Django Formsets for one-to-many relationships (e.g., Quiz Questions and Choices).
- **DRY Principle**: Do not repeat code. Use abstract base models and utility functions where appropriate.

## Additional Constraints

[ADDITIONAL_CONSTRAINTS]
<!-- TODO(ADDITIONAL_CONSTRAINTS): Intentionally deferred - no extra deployment or generic tech stack requirements provided beyond Django. -->

## Governance

- **Amendment Procedure**: Any changes to these core principles must be proposed in a PR updating this Constitution.
- **Versioning Policy**: The Constitution follows SemVer. MAJOR for breaking governance changes, MINOR for new principles, PATCH for clarifications.
- **Compliance Review**: All code PRs and design plans (`plan.md`) MUST include a checklist verifying alignment with the 5 core principles.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2026-04-03
