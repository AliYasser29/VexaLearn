# Data Model & Schema Maps: Chat & Video Features

*Note: No physical structure changes strictly. Relationships heavily leveraged.*

## `User` reverse relationships queried
The new relational filtering heavily relies on implicit reverse mappings derived natively inside `django.contrib.auth`:
- `student_profile` -> `Student`
- `teacher_profile` -> `Teacher`
- `supervisor_profile` -> `Supervisor`

### `chat_room` Logic Map
**Teacher Context**: `Student` where `enrollments.course.teacher = self`
**Student Context**: 
- `Teacher` where `course.enrollments.student = self`
- `Student` where `enrollment.course` overlaps `self.enrollment.course`
- `Supervisor` mapping broadly.

## `video_call_view` Pre-Generation Guard
1. Extracts `course_id` query params.
2. If `request.user` is a Teacher -> Check `Course.objects.filter(id=..., teacher=request.user)`.
3. If `request.user` is a Student -> Check `Enrollment.objects.filter(student=..., course=...)`.
