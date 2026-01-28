import secrets
import string
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.conf import settings
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

# استيراد الموديلات (تم إضافة الموديلات الجديدة هنا)
from .models import (
    Teacher, Student, Country, EducationType, Course, 
    Enrollment, AcademicYear, Attendance, Academy, 
    Message, Supervisor, Manager, DailyReport,
    Subject, CourseMaterial, Notification # <-- الجديد
)

# --- دالة مساعدة لتوليد باسوورد عشوائي ---
def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

# --- كلاس أساسي لتوحيد منطق إنشاء المستخدم وإرسال الإيميل ---
class BaseRoleAdmin(ModelAdmin):
    """
    كلاس يقوم بإنشاء المستخدم تلقائياً ويرسل رسالة مخصصة بالكامل لكل دور.
    """
    exclude = ('user',)
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        # 1. التنفيذ فقط عند الإضافة الجديدة
        if not change and not obj.user:
            try:
                # --- أ) إنشاء المستخدم والباسوورد ---
                password = generate_random_password()
                username = obj.phone
                
                # حل مشكلة تكرار اسم المستخدم
                if User.objects.filter(username=username).exists():
                    username = username + "_" + str(secrets.randbelow(100))

                # إنشاء اليوزر في دجانجو
                user = User.objects.create_user(username=username, password=password)
                
                # ضبط الاسم والإيميل
                if obj.name:
                    full_name_parts = obj.name.split()
                    user.first_name = full_name_parts[0]
                    if len(full_name_parts) > 1:
                        user.last_name = full_name_parts[-1]
                
                if hasattr(obj, 'email') and obj.email:
                    user.email = obj.email
                
                user.save()
                obj.user = user # ربط الكائن بالمستخدم

                # --- ب) إعداد الرسالة المنفصلة تماماً ---
                if hasattr(obj, 'email') and obj.email:
                    site_url = request.build_absolute_uri('/')
                    
                    # 1️⃣ رسالة المعلم (Teacher)
                    if isinstance(obj, Teacher):
                        subject = f'📚 انضمام لطاقم التدريس - {obj.name}'
                        # ملاحظة: تم تعديل {obj.subject} هنا لعدم وجود الحقل النصي، سيتم استخدام كلمة عامة
                        # أو يمكنك جلب أول مادة بعد الحفظ، لكن للتبسيط سنبقي الرسالة منطقية
                        message = f"""
                        مرحباً أستاذ/ة {obj.name}،

                        يسعدنا انضمامك إلينا في "VexaLearn" كمعلم.
                        
                        لقد تم إنشاء حساب خاص بك يمكنك من خلاله:
                        - التواصل مع طلابك.
                        - متابعة جدول الحصص.
                        - رفع التقارير اليومية وتسجيل الغياب.

                        بيانات الدخول الخاصة بك:
                        --------------------------------
                
                        👤 اسم المستخدم: 
                        {username}
                        🔑 كلمة المرور: 
                        {password}
                        
                        --------------------------------
                        🔗 رابط منصة التواصل: {request.build_absolute_uri('/chat')}
                        🔗رابط المنصة: {request.build_absolute_uri('/')}

                        نتمنى لك رحلة تعليمية موفقة ومثمرة.
                        إدارة الشؤون الأكاديمية
                        """

                    # 2️⃣ رسالة المشرف (Supervisor)
                    elif isinstance(obj, Supervisor):
                        subject = f'🛡️ حساب الإشراف والمتابعة - {obj.name}'
                        message = f"""
                        السيد/ة المشرف الأكاديمي: {obj.name}،

                        تم تفعيل حسابكم الإشرافي على المنصة.
                        دوركم محوري في ضمان جودة العملية التعليمية.
                        
                        صلاحيات حسابكم تشمل:
                        - مراقبة أداء الطلاب والمعلمين المسندين إليكم.
                        - مراجعة التقارير اليومية.
                        - الاطلاع على سجلات الحضور والغياب.

                        بيانات الدخول:
                        --------------------------------
                    
                        👤 اسم المستخدم: 
                        {username}
                        🔑 كلمة المرور: 
                        {password}

                        --------------------------------
                        🔗 رابط منصة التواصل: {request.build_absolute_uri('/chat')}
                        🔗 رابط منصة المتابعة {request.build_absolute_uri('/dashboard')}
                        🔗رابط المنصة: {request.build_absolute_uri('/')}
                        مع خالص التقدير،
                        إدارة المنصة
                        """

                    # 3️⃣ رسالة المدير الإداري (Manager)
                    elif isinstance(obj, Manager):
                        subject = f'🔑 بيانات الحساب الإداري - {obj.name}'
                        message = f"""
                        أهلاً بك {obj.name}،

                        هذه رسالة آلية تفيد بإنشاء حساب "مدير إداري" خاص بك.
                        لديك الآن الصلاحيات الكاملة للدخول إلى لوحة التحكم وإدارة النظام.

                        يرجى الحفاظ على سرية البيانات التالية لأهميتها القصوى:

                        ================================
                        
                        👤 اسم المستخدم: 
                        {username}
                        🔑 كلمة المرور: 
                        {password}

                        ================================
                        🔗 رابط منصة التواصل: {request.build_absolute_uri('/chat')}
                        🔗 رابط منصة اضافة الطلاب: {request.build_absolute_uri('/admin-panel')}
                        🔗رابط المنصة: {request.build_absolute_uri('/')}
                        """

                    # حالة افتراضية (احتياطي)
                    else:
                        subject = f'بيانات الحساب الجديد - {obj.name}'
                        message = f"""
                        مرحباً {obj.name}،
                        تم تسجيل حسابك بنجاح.
                        
                        
                        User: 
                        {username}
                        Pass: 
                        {password}
                        """

                    # --- ج) إرسال الإيميل ---
                    try:
                        send_mail(subject, message, settings.EMAIL_HOST_USER, [obj.email])
                        self.message_user(request, f"تم إرسال إيميل الترحيب المخصص لـ {obj.name} ✅")
                    except Exception as e:
                        self.message_user(request, f"تم الحفظ ولكن فشل إرسال الإيميل: {e}", level='warning')

            except Exception as e:
                self.message_user(request, f"حدث خطأ أثناء الإنشاء الآلي: {e}", level='error')

        # حفظ الكائن في قاعدة البيانات
        super().save_model(request, obj, form, change)


# إلغاء تسجيل User الافتراضي لتسجيله مع Unfold
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Academy)
class AcademyAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

# --- الجديد: تسجيل المواد الدراسية ---
@admin.register(Subject)
class SubjectAdmin(ModelAdmin):
    list_display = ('name', 'education_type', 'country')
    list_filter = ('country', 'education_type')
    search_fields = ('name',)
    autocomplete_fields = ['education_type', 'country']

# --- تطبيق الوراثة من BaseRoleAdmin ---

@admin.register(Teacher)
class TeacherAdmin(BaseRoleAdmin):
    # [تعديل هام]: استبدال subject بدالة get_subjects لأن الحقل أصبح ManyToMany
    list_display = ('name', 'get_subjects', 'phone', 'email', 'user')
    search_fields = ['name', 'subjects__name', 'phone']
    autocomplete_fields = ['subjects'] # للإكمال التلقائي للمواد

    def get_subjects(self, obj):
        return ", ".join([sub.name for sub in obj.subjects.all()])
    get_subjects.short_description = "المواد"

@admin.register(Supervisor)
class SupervisorAdmin(BaseRoleAdmin): 
    list_display = ('name', 'phone', 'email', 'user')
    search_fields = ['name', 'phone']

@admin.register(Manager)
class ManagerAdmin(BaseRoleAdmin):
    list_display = ('name', 'phone', 'email', 'user')
    search_fields = ['name', 'phone']

# ------------------------------------------------------------------

@admin.register(Country)
class CountryAdmin(ModelAdmin):
    list_display = ('name', 'currency')
    search_fields = ['name']

@admin.register(EducationType)
class EducationTypeAdmin(ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ['name']
    autocomplete_fields = ['country']

@admin.register(AcademicYear)
class AcademicYearAdmin(ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ['name']
    autocomplete_fields = ['country']

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    # [تعديل]: إضافة subject للقائمة
    list_display = ('name', 'subject', 'price', 'country', 'academy', 'sessions_count')
    list_filter = ('country', 'payment_type', 'academy', 'subject')
    search_fields = ['name']
    autocomplete_fields = ['country', 'academy', 'subject']

# تعريف Inline قبل استخدامه
class EnrollmentInline(StackedInline):
    model = Enrollment
    extra = 1
    autocomplete_fields = ['course', 'teacher'] # [تعديل]: إضافة teacher

@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    # [تعديل]: إضافة teacher للعرض
    list_display = ('student', 'course', 'teacher', 'start_date', 'attendance_summary', 'is_completed')
    list_filter = ('is_completed', 'course', 'start_date', 'teacher')
    search_fields = ('student__name', 'course__name', 'teacher__name')
    autocomplete_fields = ['student', 'course', 'teacher']
    
    def attendance_summary(self, obj):
        present = obj.attendances.filter(status='present').count()
        absent = obj.attendances.filter(status='absent').count()
        return f"✅ {present} | ❌ {absent}"
    attendance_summary.short_description = "حضور | غياب"

    class AttendanceInline(TabularInline):
        model = Attendance
        extra = 0
        readonly_fields = ('date', 'status')
        can_delete = True
    
    inlines = [AttendanceInline]

@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ('enrollment', 'date', 'status')
    list_filter = ('date', 'status', 'enrollment__course')
    search_fields = ('enrollment__student__name',)
    autocomplete_fields = ['enrollment']

@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = ('name', 'academic_year', 'country', 'parent_phone', 'user', 'supervisor')
    search_fields = ('name', 'parent_name', 'parent_phone')
    list_filter = ('country', 'education_type', 'academic_year', 'supervisor')
    
    exclude = ('user',)
    readonly_fields = ('user',)
    
    inlines = [EnrollmentInline]
    
    autocomplete_fields = ['country', 'education_type', 'academic_year', 'teachers', 'supervisor']

@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(DailyReport)
class DailyReportAdmin(ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'has_attachment')
    list_filter = ('date', 'teacher', 'student')
    search_fields = ('student__name', 'teacher__name', 'content')
    date_hierarchy = 'date'
    
    def has_attachment(self, obj):
        return "✅" if obj.attachment else "❌"
    has_attachment.short_description = "مرفق"

# --- الجديد: إدارة مكتبة المواد ---
@admin.register(CourseMaterial)
class CourseMaterialAdmin(ModelAdmin):
    list_display = ('title', 'course', 'teacher', 'created_at')
    list_filter = ('course', 'teacher')
    search_fields = ('title', 'course__name')
    autocomplete_fields = ['course', 'teacher']

# --- الجديد: إدارة الإشعارات ---
@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('recipient', 'title', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
