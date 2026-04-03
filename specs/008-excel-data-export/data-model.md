# Data Model: Excel Data Export

This feature does not introduce new database tables or modify existing schemas. It defines **Resource Classes** that dictate how existing entities are serialized into Excel files.

## Resource Definitions (`core/resources.py`)

### `StudentResource`
- **Model**: `Student`
- **Fields to Export**: `id`, `name`, `parent_name`, `parent_phone`, `student_phone`, `country`, `education_type`, `academic_year`
- **Transformations**: 
  - `country` -> Resolves to `country.name`
  - `education_type` -> Resolves to `education_type.name`
  - `academic_year` -> Resolves to `academic_year.name`

### `TeacherResource`
- **Model**: `Teacher`
- **Fields to Export**: `id`, `name`, `phone`, `email`
- **Transformations**: 
  - `subjects` (M2M) -> Resolves to a comma-separated list of subject names.

### `EnrollmentResource`
- **Model**: `Enrollment`
- **Fields to Export**: `id`, `student`, `course`, `teacher`, `start_date`, `is_completed`
- **Transformations**:
  - `student` -> Resolves to `student.name`
  - `course` -> Resolves to `course.name`
  - `teacher` -> Resolves to `teacher.name` (or empty if None)

### `AttendanceResource`
- **Model**: `Attendance`
- **Fields to Export**: `id`, `student_name`, `course_name`, `date`, `status`
- **Transformations**:
  - Requires traversing the relationship: `enrollment.student.name` and `enrollment.course.name`.
  - `status` -> Resolves to the human-readable display value ("حضور" or "غياب").
