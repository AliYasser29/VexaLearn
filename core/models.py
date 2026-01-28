import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.conf import settings
from .utils import send_mail_async 

# 1. الدولة (يجب أن تكون في البداية لأن الجميع يعتمد عليها)
class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الدولة")
    currency = models.CharField(max_length=10, verbose_name="العملة (EGP, USD)")
    
    def __str__(self): return f"{self.name} ({self.currency})"
    class Meta: verbose_name = "دولة"; verbose_name_plural = "الدول"

# 2. نوع التعليم
class EducationType(models.Model):
    name = models.CharField(max_length=100, verbose_name="نوع التعليم")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='education_types', verbose_name="تابع لدولة")
    
    def __str__(self): return f"{self.name} ({self.country.name})"
    class Meta: verbose_name = "نوع تعليم"; verbose_name_plural = "أنواع التعليم"

# 3. السنة الدراسية
class AcademicYear(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم السنة (مثال: الصف الأول الثانوي)")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='academic_years', verbose_name="تابع لدولة")

    def __str__(self): return f"{self.name} ({self.country.name})"
    class Meta: verbose_name = "سنة دراسية"; verbose_name_plural = "السنوات الدراسية"

# 4. المادة الدراسية (جديد)
class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المادة")
    education_type = models.ForeignKey(EducationType, on_delete=models.CASCADE, verbose_name="نوع التعليم")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="الدولة")

    def __str__(self):
        return f"{self.name} - {self.education_type.name}"
    
    class Meta: verbose_name = "مادة دراسية"; verbose_name_plural = "المواد الدراسية"

# 5. الأكاديمية
class Academy(models.Model):
    name = models.CharField(max_length=150, verbose_name="اسم الأكاديمية")
    description = models.TextField(verbose_name="وصف الأكاديمية", null=True, blank=True, help_text="نبذة مختصرة تظهر في الصفحة الرئيسية")
    logo = models.ImageField(upload_to='academy_logos/', null=True, blank=True, verbose_name="شعار الأكاديمية")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "أكاديمية"
        verbose_name_plural = "الأكاديميات"

# 6. المعلم (محدث)
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='teacher_profile', verbose_name="حساب المستخدم")
    name = models.CharField(max_length=150, verbose_name="اسم المعلم")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني", null=True, blank=True)
    
    # التعديل: المعلم يدرس عدة مواد (M2M) بدلاً من نص ثابت
    subjects = models.ManyToManyField(Subject, related_name='teachers', verbose_name="المواد التي يدرسها")
    
    bio = models.TextField(blank=True, null=True, verbose_name="نبذة عن المعلم")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return self.name
    class Meta: verbose_name = "معلم"; verbose_name_plural = "المعلمون"

# 7. المشرف
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='supervisor_profile', verbose_name="حساب المستخدم")
    name = models.CharField(max_length=150, verbose_name="اسم المشرف")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني", null=True, blank=True)
    
    def __str__(self): return self.name
    class Meta: verbose_name = "مشرف"; verbose_name_plural = "المشرفون"

# 8. المدير الإداري
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='manager_profile', verbose_name="حساب المستخدم")
    name = models.CharField(max_length=150, verbose_name="اسم المدير")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(verbose_name="البريد الإلكتروني", null=True, blank=True)
    
    def __str__(self): return self.name
    class Meta: verbose_name = "مدير إداري"; verbose_name_plural = "المديرون الإداريون"

# 9. الكورس (محدث)
class Course(models.Model):
    PAYMENT_CHOICES = [('monthly', 'دفع شهري'), ('full', 'دفع كامل (مرة واحدة)')]
    name = models.CharField(max_length=150, verbose_name="اسم الكورس")
    academic_years = models.ManyToManyField(AcademicYear, verbose_name="السنوات الدراسية", blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المادة الدراسية")
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    duration_months = models.IntegerField(default=1, verbose_name="مدة الكورس (بالأشهر)")
    sessions_count = models.IntegerField(default=8, verbose_name="عدد الحصص في الكورس")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='monthly', verbose_name="نظام الدفع")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='courses')
    academy = models.ForeignKey(Academy, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name="الأكاديمية")
    
    description = models.TextField(verbose_name="وصف الكورس", null=True, blank=True)

    def __str__(self): return f"{self.name} | {self.price} {self.country.currency}"
    class Meta: verbose_name = "كورس"; verbose_name_plural = "الكورسات"

# 10. الطالب
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile', verbose_name="حساب المستخدم")
    name = models.CharField(max_length=150, verbose_name="اسم الطالب")
    age = models.IntegerField(verbose_name="العمر")
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, verbose_name="السنة الدراسية")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name="الدولة")
    education_type = models.ForeignKey(EducationType, on_delete=models.SET_NULL, null=True, verbose_name="نوع التعليم")

    parent_name = models.CharField(max_length=150, verbose_name="اسم ولي الأمر")
    parent_phone = models.CharField(max_length=20, verbose_name="رقم هاتف ولي الأمر")
    parent_email = models.EmailField(verbose_name="ايميل ولي الأمر")
    
    # ملاحظة: هذه العلاقة يمكن الإبقاء عليها للوصول السريع، لكن العلاقة الأدق أصبحت في Enrollment
    teachers = models.ManyToManyField(Teacher, blank=True)
    
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name="المشرف المسؤول")
    
    courses = models.ManyToManyField(Course, through='Enrollment', verbose_name="الكورسات المسجلة")

    def __str__(self): return self.name

    def clean(self):
        super().clean()
        if self.country:
            if self.education_type and self.education_type.country != self.country:
                 raise ValidationError({'education_type': "نوع التعليم يجب أن يطابق الدولة المختارة."})
            if self.academic_year and self.academic_year.country != self.country:
                 raise ValidationError({'academic_year': "السنة الدراسية يجب أن تطابق الدولة المختارة."})

    class Meta: verbose_name = "طالب"; verbose_name_plural = "الطلاب"

# 11. الاشتراكات (محدث)
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="الكورس")
    
    # التعديل: تحديد المعلم عند الاشتراك
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name="المعلم المختار")
    
    start_date = models.DateField(default=timezone.now, verbose_name="تاريخ بدء الاشتراك")
    is_completed = models.BooleanField(default=False, verbose_name="منتهي")

    def __str__(self):
        teacher_name = self.teacher.name if self.teacher else "بدون معلم"
        return f"{self.student.name} - {self.course.name} ({teacher_name})"

    def get_progress_percent(self):
        total_sessions = self.course.sessions_count
        if total_sessions == 0: return 0
        attended_count = self.attendances.count()
        percent = (attended_count / total_sessions) * 100
        return min(percent, 100)
    
    class Meta:
        verbose_name = "اشتراك"
        verbose_name_plural = "الاشتراكات"

# 12. الحضور
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'حضور'),
        ('absent', 'غياب'),
    ]
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendances', verbose_name="الاشتراك")
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ الحصة")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', verbose_name="الحالة")

    def __str__(self): 
        return f"{self.enrollment.student.name} - {self.date} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = "سجل حصة"
        verbose_name_plural = "سجلات الحضور والغياب"
        unique_together = ('enrollment', 'date')

# 13. الرسائل (نظام الشات)
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="المرسل")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="المستقبل")
    content = models.TextField(verbose_name="نص الرسالة")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإرسال")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة")

    def __str__(self):
        return f"من {self.sender} إلى {self.receiver}"

    class Meta:
        ordering = ['timestamp']
        verbose_name = "رسالة"
        verbose_name_plural = "الرسائل"

# 14. التقارير اليومية
class DailyReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_reports', verbose_name="الطالب")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='submitted_reports', verbose_name="المعلم")
    content = models.TextField(verbose_name="محتوى التقرير")
    attachment = models.FileField(upload_to='daily_reports/', null=True, blank=True, verbose_name="ملف مرفق")
    date = models.DateField(default=timezone.now, verbose_name="تاريخ التقرير")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الرفع")

    def __str__(self):
        return f"تقرير عن {self.student.name} - {self.date}"

    class Meta:
        verbose_name = "تقرير يومي"
        verbose_name_plural = "التقارير اليومية"
        ordering = ['-created_at']
        unique_together = ('student', 'teacher', 'date')

# 15. المواد التعليمية (جديد - لرفع الملفات)
class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials', verbose_name="الكورس")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="المعلم")
    title = models.CharField(max_length=200, verbose_name="عنوان الملف")
    description = models.TextField(blank=True, null=True, verbose_name="وصف (اختياري)")
    file = models.FileField(upload_to='materials/%Y/%m/', verbose_name="الملف")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.name}"

    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()
    
    def icon_class(self):
        ext = self.file_extension()
        if ext == '.pdf': return 'fa-file-pdf text-danger'
        if ext in ['.doc', '.docx']: return 'fa-file-word text-primary'
        if ext in ['.xls', '.xlsx']: return 'fa-file-excel text-success'
        if ext in ['.ppt', '.pptx']: return 'fa-file-powerpoint text-warning'
        if ext in ['.zip', '.rar']: return 'fa-file-archive text-secondary'
        if ext in ['.jpg', '.png', '.jpeg']: return 'fa-file-image text-info'
        return 'fa-file-alt text-dark'
    
    class Meta:
        verbose_name = "مادة علمية"
        verbose_name_plural = "المكتبة والمواد"

# 16. الإشعارات (جديد)
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"إشعار لـ {self.recipient.username} - {self.title}"
    
    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"

# --- Signals ---

@receiver(post_save, sender=Student)
def notify_supervisor_new_student(sender, instance, created, **kwargs):
    if created and instance.supervisor and instance.supervisor.email:
        # نستخدم رابطاً ثابتاً أو نجلبه من الإعدادات
        site_url = "https://vexalearn.cloud"  # أو settings.CSRF_TRUSTED_ORIGINS[0]
        
        subject = f'تنبيه: تم إسناد طالب جديد إليك - {instance.name}'
        message = f"""
        مرحباً {instance.supervisor.name}،
        
        تم تسجيل طالب جديد وإسناده لإشرافك.
        
        بيانات الطالب:
        --------------------------
        الاسم: {instance.name}
        السنة الدراسية: {instance.academic_year}
        --------------------------
        
        يرجى متابعة الطالب من خلال لوحة التحكم.
        رابط المنصة: {site_url}/dashboard
        """
        send_mail_async(subject, message, [instance.supervisor.email])
        print(f"✅ تم جدولة إرسال الإيميل للمشرف: {instance.supervisor.name}")


# تعديل الدالة الثانية
@receiver(m2m_changed, sender=Student.teachers.through)
def notify_teachers_new_student(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        new_teachers = Teacher.objects.filter(pk__in=pk_set)
        # نستخدم رابطاً ثابتاً
        site_url = "https://vexalearn.cloud" 

        for teacher in new_teachers:
            if teacher.email:
                subject = f'طالب جديد في مجموعتك - {instance.name}'
                message = f"""
                مرحباً أستاذ/ة {teacher.name}،
                
                تم إضافة الطالب ({instance.name}) إلى قائمة طلابك.
                
                بيانات الطالب:
                --------------------------
                الاسم: {instance.name}
                السنة الدراسية: {instance.academic_year}
                --------------------------
                
                يرجى التواصل معه ومتابعة تقدمه.
                {site_url}/chat
                """
                send_mail_async(subject, message, [teacher.email])
                print(f"✅ تم جدولة إرسال الإيميل للمعلم: {teacher.name}")

@receiver(post_save, sender=Attendance)
def notify_attendance_change(sender, instance, created, **kwargs):
    if created:
        enrollment = instance.enrollment
        student = enrollment.student
        course = enrollment.course
        parent_email = student.parent_email

        if parent_email:
            # 1. الحسابات
            current_session_number = enrollment.attendances.count()
            total_sessions = course.sessions_count
            remaining_sessions = total_sessions - current_session_number
            if remaining_sessions < 0: remaining_sessions = 0

            # 2. منطق التنبيه
            renewal_notice = ""
            if total_sessions > 0:
                threshold = total_sessions * 0.25
                if remaining_sessions <= threshold and remaining_sessions > 0:
                    renewal_notice = """
                    🔴 تنبيه هام:
                    لقد شارف الاشتراك على الانتهاء. يرجى مراجعة الإدارة لتجديد الاشتراك.
                    """
                elif remaining_sessions == 0:
                    renewal_notice = """
                    🔴 تنبيه هام:
                    لقد انتهت جميع حصص هذا الكورس. يرجى التجديد فوراً.
                    """

            status_text = "حضور ✅" if instance.status == 'present' else "غياب ❌"

            subject = f'تنبيه حصة: {student.name} - كورس {course.name}'
            message = f"""
            مرحباً ولي أمر الطالب/ة {student.name}،
            
            نود إعلامكم بأنه تم تسجيل "{status_text}" للطالب اليوم في كورس {course.name}.
            
            تفاصيل الحصة:
            --------------------------------------------------
            الحالة: {status_text}
            رقم الحصة: {current_session_number} من أصل {total_sessions}
            المتبقي في الكورس: {remaining_sessions} حصص
            --------------------------------------------------
            {renewal_notice}
            
            تاريخ التسجيل: {instance.date}
            
            إدارة الأكاديمية
            """
            send_mail_async(subject, message, [parent_email])
            print(f"✅ تم جدولة إشعار الحضور لولي الأمر: {parent_email}")


@receiver(post_delete, sender=Teacher)
@receiver(post_delete, sender=Student)
@receiver(post_delete, sender=Supervisor)
@receiver(post_delete, sender=Manager)
def disable_user_on_profile_delete(sender, instance, **kwargs):
    """
    دالة موحدة تعمل عند حذف أي بروفايل (معلم، طالب، مشرف، مدير).
    تقوم بتعطيل حساب المستخدم (User) المرتبط بهذا البروفايل فوراً.
    """
    try:
        if instance.user:
            user = instance.user
            
            # حماية: عدم تعطيل السوبر يوزر
            if user.is_superuser:
                print(f"تنبيه: تم حذف بروفايل للسوبر يوزر {user.username} ولكن لم يتم تعطيل الحساب.")
                return

            # تعطيل الحساب
            user.is_active = False
            user.save()
            
            print(f"✅ تم تعطيل حساب المستخدم '{user.username}' تلقائياً بعد حذف دوره كـ {sender.__name__}.")
            
    except Exception as e:
        print(f"حدث خطأ أثناء محاولة تعطيل المستخدم: {e}")
