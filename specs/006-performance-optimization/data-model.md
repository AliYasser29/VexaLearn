# Data Model: Performance Optimization

This feature does not introduce new entities or modify the database schema. Instead, it optimizes how existing entities are queried and retrieved.

## Optimized Entities & Relationships

### `Enrollment`
- **Current Issue**: Fetched without related `Course` or `Attendance` data, leading to N+1 queries.
- **Optimization**: All `Enrollment` queries in list views and dashboards must use `.select_related('course', 'student', 'teacher')` and `.prefetch_related('attendances')`.

### `Student`
- **Current Issue**: Fetching `enrollment_set` triggers N+1 if not properly prefetched with nested relations.
- **Optimization**: Use `Prefetch('enrollment_set', queryset=Enrollment.objects.select_related('course').prefetch_related('attendances'))`.

### `CourseMaterial`
- **Current Issue**: Library filtering queries can be slow.
- **Optimization**: Use `.select_related('course', 'teacher')` when querying materials to avoid N+1 lookups on the course name and teacher details.
