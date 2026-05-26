from django import forms
from .models import (
    CourseMaterial, Student, Enrollment, DailyReport, 
    Course, Subject, Supervisor, Teacher
)

# --- 1. فورم إضافة وتعديل الطالب ---
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 
            'age',
            'parent_name', 
            'parent_phone', 
            'parent_email', 
            'country', 
            'education_type', 
            'academic_year', 
            'supervisor'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'اسم الطالب رباعي'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-input'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-input', 'required': 'required'}),
            'country': forms.Select(attrs={'class': 'form-input'}),
            'education_type': forms.Select(attrs={'class': 'form-input'}),
            'academic_year': forms.Select(attrs={'class': 'form-input'}),
            'supervisor': forms.Select(attrs={'class': 'form-input'}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تخصيص القائمة المنسدلة للمشرفين
        self.fields['supervisor'].queryset = Supervisor.objects.all()
        self.fields['supervisor'].empty_label = "اختر المشرف المسؤول (اختياري)"
        self.fields['supervisor'].required = False

# --- 2. فورم تسجيل المواد (الاشتراكات) ---
class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'teacher']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control', 'id': 'id_course'}),
            'teacher': forms.Select(attrs={'class': 'form-control', 'id': 'id_teacher'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.none()

        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                selected_course = Course.objects.get(id=course_id)
                # جلب المعلمين المرتبطين بمادة الكورس
                if selected_course.subject:
                    self.fields['teacher'].queryset = selected_course.subject.teachers.all()
                else:
                    self.fields['teacher'].queryset = Teacher.objects.all()
            except (ValueError, TypeError, Course.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.course:
            # في حالة التعديل، إظهار معلمي المادة الحالية
             if self.instance.course.subject:
                self.fields['teacher'].queryset = self.instance.course.subject.teachers.all()

# --- 3. فورم التقرير اليومي ---
class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب ملاحظاتك عن الطالب اليوم...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError("حجم المرفق يجب ألا يتجاوز 10 ميجابايت.")
            
            allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(attachment.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError("امتداد الملف المرفق غير مدعوم أو غير آمن.")
        return attachment

# --- 4. فورم المعلم (لإدارة المواد) ---
class TeacherForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        label="المواد التي يدرسها"
    )

    class Meta:
        model = Teacher
        fields = ['name', 'phone', 'subjects', 'bio'] 

# --- 5. فورم رفع المواد العلمية (لالمكتبة) ---
class MaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['course', 'title', 'description', 'file']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: ملخص الوحدة الأولى'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف اختياري...'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("حجم الملف يجب ألا يتجاوز 10 ميجابايت.")
            
            allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError("امتداد الملف غير مدعوم أو غير آمن.")
        return file

    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            teacher_subjects = teacher.subjects.all()
            self.fields['course'].queryset = Course.objects.filter(subject__in=teacher_subjects)