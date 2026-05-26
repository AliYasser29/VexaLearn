import secrets
import string
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.tasks import send_email_task
from django.conf import settings
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from simple_history.admin import SimpleHistoryAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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

from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from .resources import StudentResource, TeacherResource, EnrollmentResource, AttendanceResource

# --- كلاس أساسي لتوحيد منطق إنشاء المستخدم وإرسال الإيميل ---
class BaseRoleAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
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
                
                import re
                # جلب رقم الهاتف والبريد المناسب بناءً على نوع الكائن
                if isinstance(obj, Student):
                    raw_phone = obj.parent_phone or ''
                    target_email = obj.parent_email
                    role_prefix = 'student'
                else:
                    raw_phone = obj.phone or ''
                    target_email = obj.email if hasattr(obj, 'email') else None
                    if isinstance(obj, Teacher):
                        role_prefix = 'teacher'
                    elif isinstance(obj, Supervisor):
                        role_prefix = 'supervisor'
                    else:
                        role_prefix = 'manager'

                # تنظيف رقم الهاتف وإبقاء الحروف اللاتينية والأرقام فقط لتجنب مشاكل تشفير أسماء المستخدمين
                username = re.sub(r'[^a-zA-Z0-9]', '', raw_phone)
                if not username:
                    username = f"{role_prefix}_{secrets.token_hex(4)}"
                
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
                
                if target_email:
                    user.email = target_email
                
                user.save()
                obj.user = user # ربط الكائن بالمستخدم

                # --- ب) إعداد الرسالة المنفصلة تماماً ---
                if target_email:
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

                    # 4️⃣ رسالة الطالب (Student)
                    elif isinstance(obj, Student):
                        subject = f'🔑 بيانات الحساب للطالب/ة - {obj.name}'
                        message = f"""
                        مرحباً ولي أمر الطالب/ة {obj.name}،
                        
                        تم تسجيل حساب الطالب بنجاح في المنصة.
                        
                        بيانات الدخول الخاصة بالطالب:
                        --------------------------------
                        
                        👤 اسم المستخدم: 
                        {username}
                        🔑 كلمة المرور: 
                        {password}
                        
                        --------------------------------
                        🔗 رابط المنصة: {site_url}
                        
                        يرجى الاحتفاظ بهذه البيانات لمتابعة الدروس والتواصل.
                        إدارة المنصة
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
                        send_email_task.delay(subject, message, [target_email])
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
class AcademyAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

# --- الجديد: تسجيل المواد الدراسية ---
@admin.register(Subject)
class SubjectAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'education_type', 'country')
    list_filter = ('country', 'education_type')
    search_fields = ('name',)
    autocomplete_fields = ['education_type', 'country']

# --- تطبيق الوراثة من BaseRoleAdmin ---

@admin.register(Teacher)
class TeacherAdmin(BaseRoleAdmin):
    resource_classes = [TeacherResource]
    # [تعديل هام]: استبدال subject بدالة get_subjects لأن الحقل أصبح ManyToMany
    list_display = ('name', 'get_subjects', 'phone', 'email', 'user', 'get_student_count')
    search_fields = ['name', 'subjects__name', 'phone', 'email', 'user__username']
    list_filter = ['subjects']
    list_per_page = 50
    autocomplete_fields = ['subjects'] # للإكمال التلقائي للمواد

    def get_queryset(self, request):
        # Prevent N+1 queries when fetching related subjects and enrollments
        return super().get_queryset(request).select_related('user').prefetch_related('subjects', 'enrollment_set')

    def get_subjects(self, obj):
        return ", ".join([sub.name for sub in obj.subjects.all()])
    get_subjects.short_description = "المواد"

    def get_student_count(self, obj):
        return obj.enrollment_set.filter(is_completed=False).count()
    get_student_count.short_description = "عدد الطلاب الحاليين"

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
class CountryAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'currency')
    search_fields = ['name']

@admin.register(EducationType)
class EducationTypeAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ['name']
    autocomplete_fields = ['country']

@admin.register(AcademicYear)
class AcademicYearAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ['name']
    autocomplete_fields = ['country']

@admin.register(Course)
class CourseAdmin(SimpleHistoryAdmin, ModelAdmin):
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
class EnrollmentAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    resource_classes = [EnrollmentResource]
    # [تعديل]: إضافة teacher للعرض
    list_display = ('student', 'course', 'teacher', 'start_date', 'attendance_summary', 'is_completed')
    list_filter = ('is_completed', 'course', 'start_date', 'teacher')
    search_fields = ('student__name', 'course__name', 'teacher__name')
    autocomplete_fields = ['student', 'course', 'teacher']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'course', 'teacher').prefetch_related('attendances')

    
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
class AttendanceAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    resource_classes = [AttendanceResource]
    list_display = ('enrollment', 'date', 'status')
    list_filter = ('date', 'status', 'enrollment__course')
    search_fields = ('enrollment__student__name',)
    autocomplete_fields = ['enrollment']

@admin.register(Student)
class StudentAdmin(BaseRoleAdmin):
    resource_classes = [StudentResource]
    change_list_template = "admin/core/student/change_list.html"
    list_display = ('name', 'academic_year', 'country', 'parent_phone', 'user', 'supervisor', 'get_courses_and_attendance')

    search_fields = ('name', 'parent_name', 'parent_phone', 'user__username', 'user__email')
    list_filter = ('country', 'education_type', 'academic_year', 'supervisor', 'teachers')
    list_per_page = 50
    
    inlines = [EnrollmentInline]
    
    autocomplete_fields = ['country', 'education_type', 'academic_year', 'teachers', 'supervisor']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Get current view from GET parameters, default to 'table'
        current_view = request.GET.get('view', 'table')
        if current_view not in ['table', 'grid']:
            current_view = 'table'
            
        extra_context['current_view'] = current_view
        
        # Build query dicts for URLs to preserve filters
        query_params = request.GET.copy()
        
        # Build Table View URL
        query_params['view'] = 'table'
        extra_context['table_view_url'] = f"?{query_params.urlencode()}"
        
        # Build Grid View URL
        query_params['view'] = 'grid'
        extra_context['grid_view_url'] = f"?{query_params.urlencode()}"
        
        # CRITICAL: Django Admin ChangeList parses all GET parameters as field lookups.
        # We must remove 'view' from request.GET before calling super() to prevent FieldError / DatabaseError!
        if 'view' in request.GET:
            request.GET = request.GET.copy()
            request.GET.pop('view', None)
            
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        # Prevent N+1 queries when fetching related enrollments and attendances for the custom column
        return super().get_queryset(request).select_related('academic_year', 'country', 'supervisor', 'user').prefetch_related('enrollment_set__course', 'enrollment_set__attendances')

    def get_courses_and_attendance(self, obj):
        enrollments = obj.enrollment_set.all()
        if not enrollments:
            return "لا يوجد"
        
        badges = []
        for e in enrollments:
            attended = sum(1 for a in e.attendances.all() if a.status == 'present')
            total = e.course.sessions_count
            
            # Choose a visually stunning badge styling based on attendance ratio
            ratio = attended / total if total > 0 else 0
            if ratio >= 0.75:
                # Emerald / Green Badge
                color_class = "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 border-emerald-250 dark:border-emerald-800"
            elif ratio >= 0.5:
                # Amber / Orange Badge
                color_class = "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400 border-amber-250 dark:border-amber-800"
            else:
                # Rose / Red Badge
                color_class = "bg-rose-50 text-rose-700 dark:bg-rose-950/30 dark:text-rose-400 border-rose-250 dark:border-rose-800"
                
            badges.append(format_html(
                '<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold border {}">{} <span class="opacity-75">({}/{})</span></span>',
                color_class,
                e.course.name,
                attended,
                total
            ))
        return format_html('<div class="flex flex-wrap gap-1.5">{}</div>', mark_safe(''.join(badges)))
    get_courses_and_attendance.short_description = "الكورسات والحضور"

@admin.register(Message)
class MessageAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(DailyReport)
class DailyReportAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'has_attachment')
    list_filter = ('date', 'teacher', 'student')
    search_fields = ('student__name', 'teacher__name', 'content')
    date_hierarchy = 'date'
    
    def has_attachment(self, obj):
        return "✅" if obj.attachment else "❌"
    has_attachment.short_description = "مرفق"

# --- الجديد: إدارة مكتبة المواد ---
@admin.register(CourseMaterial)
class CourseMaterialAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('title', 'course', 'teacher', 'created_at')
    list_filter = ('course', 'teacher')
    search_fields = ('title', 'course__name')
    autocomplete_fields = ['course', 'teacher']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'teacher')

# --- الجديد: إدارة الإشعارات ---
@admin.register(Notification)
class NotificationAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('recipient', 'title', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')

# --- Global History (US2) ---
# Registering historical models directly to provide a global audit trail.
@admin.register(Student.history.model)
class StudentHistoryAdmin(ModelAdmin):
    list_display = ('history_id', 'history_date', 'history_user', 'history_type', 'name')
    list_filter = ('history_date', 'history_type', 'history_user')
    search_fields = ('name', 'history_user__username')
    readonly_fields = [f.name for f in Student.history.model._meta.get_fields()]

@admin.register(Teacher.history.model)
class TeacherHistoryAdmin(ModelAdmin):
    list_display = ('history_id', 'history_date', 'history_user', 'history_type', 'name')
    list_filter = ('history_date', 'history_type', 'history_user')
    search_fields = ('name', 'history_user__username')
    readonly_fields = [f.name for f in Teacher.history.model._meta.get_fields()]

@admin.register(Enrollment.history.model)
class EnrollmentHistoryAdmin(ModelAdmin):
    list_display = ('history_id', 'history_date', 'history_user', 'history_type', 'student', 'course')
    list_filter = ('history_date', 'history_type', 'history_user')
    search_fields = ('student__name', 'course__name', 'history_user__username')
    readonly_fields = [f.name for f in Enrollment.history.model._meta.get_fields()]
