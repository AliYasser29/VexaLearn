from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import Student, Teacher, Enrollment, Attendance

class StudentResource(resources.ModelResource):
    country = fields.Field(column_name='Country', attribute='country__name')
    education_type = fields.Field(column_name='Education Type', attribute='education_type__name')
    academic_year = fields.Field(column_name='Academic Year', attribute='academic_year__name')

    class Meta:
        model = Student
        fields = ('id', 'name', 'parent_name', 'parent_phone', 'country', 'education_type', 'academic_year')
        export_order = fields

class TeacherResource(resources.ModelResource):
    subjects = fields.Field(
        column_name='Subjects',
        attribute='subjects',
        widget=ManyToManyWidget(model='core.Subject', field='name', separator=', ')
    )

    class Meta:
        model = Teacher
        fields = ('id', 'name', 'phone', 'email', 'subjects')
        export_order = fields

class EnrollmentResource(resources.ModelResource):
    student = fields.Field(column_name='Student', attribute='student__name')
    course = fields.Field(column_name='Course', attribute='course__name')
    teacher = fields.Field(column_name='Teacher', attribute='teacher__name')

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'teacher', 'start_date', 'is_completed')
        export_order = fields

class AttendanceResource(resources.ModelResource):
    student_name = fields.Field(column_name='Student Name', attribute='enrollment__student__name')
    course_name = fields.Field(column_name='Course Name', attribute='enrollment__course__name')
    status = fields.Field(column_name='Status', attribute='get_status_display')

    class Meta:
        model = Attendance
        fields = ('id', 'student_name', 'course_name', 'date', 'status')
        export_order = fields
