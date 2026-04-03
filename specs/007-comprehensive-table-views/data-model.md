# Data Model: Comprehensive Table Views

This feature focuses on presentation and does not require new database tables or modifications to existing fields. It relies on optimizing and displaying existing relational data.

## Entities and Display Logic

### `Student` Entity (Admin Grid View)
The grid view for Students will aggregate the following:
- **Profile Data**: `name`, `parent_phone`, `country`
- **Academic Data**: `academic_year`, `education_type`
- **Enrollment Summary (Computed)**: A custom method `get_active_enrollments` will query the `Enrollment` model to return a formatted list of currently active courses for the student.

### `Teacher` Entity (Admin Grid View)
The grid view for Teachers will aggregate the following:
- **Profile Data**: `name`, `phone`, `email`
- **Academic Data**: A custom method `get_subjects` will query the M2M `subjects` relationship to return a list of taught subjects.
- **Load Summary (Computed)**: A custom method `get_student_count` will query active enrollments tied to this teacher to show their current workload.

## Performance Considerations
To ensure SC-001 (load times under 2 seconds) is met when displaying these computed fields, the `ModelAdmin.get_queryset` method MUST be overridden to use `select_related` and `prefetch_related` (as established in previous performance optimization specs).