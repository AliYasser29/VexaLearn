<<<<<<< HEAD
import time
import secrets
import string
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Prefetch, Q, Exists, OuterRef
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.http import JsonResponse
from django.conf import settings
from agora_token_builder import RtcTokenBuilder

# استيراد الأدوات المساعدة
from .utils import send_mail_async

# استيراد الموديلات
from .models import (
    Academy, Course, CourseMaterial, Student, Enrollment, Attendance, Message, 
    Teacher, Supervisor, Manager, DailyReport, Country, Notification, EducationType, AcademicYear
)

# استيراد النماذج (Forms)
from .forms import MaterialForm, StudentForm, EnrollmentForm, DailyReportForm

# محاولة استيراد موديلات الاختبارات بشكل آمن
try:
    from quiz.models import Quiz, QuizAttempt
except ImportError:
    Quiz = None
    QuizAttempt = None


# ==========================================
# 1. دوال الحضور والغياب وإنهاء الكورس
# ==========================================

@login_required
def mark_attendance(request, enrollment_id):
    """تسجيل حضور طالب في حصة معينة."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # التحقق من الصلاحية (Admin أو المشرف المسؤول)
    is_authorized = request.user.is_superuser or (
        enrollment.student.supervisor and 
        enrollment.student.supervisor.user == request.user
    )
    
    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء.")
        return redirect('supervisor_dashboard')

    if enrollment.attendances.count() >= enrollment.course.sessions_count:
        messages.error(request, "عفواً، لقد اكتمل عدد حصص هذا الكورس.")
        return redirect('supervisor_dashboard')

    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        enrollment=enrollment, 
        date=today
    )

    if created:
        attendance.status = 'present'
        attendance.save()
        messages.success(request, f"تم تسجيل ✅ حضور {enrollment.student.name}.")
        
        if enrollment.student.user:
            Notification.objects.create(
                recipient=enrollment.student.user,
                title="تسجيل حضور",
                message=f"تم تسجيل حضورك في كورس {enrollment.course.name} بتاريخ {today}."
            )
    else:
        messages.warning(request, "تم تسجيل حالة لهذا الطالب اليوم مسبقاً.")

    return redirect('supervisor_dashboard')


@login_required
def mark_absence(request, enrollment_id):
    """تسجيل غياب طالب عن حصة معينة."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    is_authorized = request.user.is_superuser or (
        enrollment.student.supervisor and 
        enrollment.student.supervisor.user == request.user
    )

    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء.")
        return redirect('supervisor_dashboard')

    if enrollment.attendances.count() >= enrollment.course.sessions_count:
        messages.error(request, "عفواً، لقد اكتمل عدد حصص هذا الكورس.")
        return redirect('supervisor_dashboard')

    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        enrollment=enrollment, 
        date=today
    )

    if created:
        attendance.status = 'absent'
        attendance.save()
        messages.warning(request, f"تم تسجيل ❌ غياب {enrollment.student.name}.")
        
        if enrollment.student.user:
            Notification.objects.create(
                recipient=enrollment.student.user,
                title="تسجيل غياب",
                message=f"تم تسجيل غيابك عن كورس {enrollment.course.name} بتاريخ {today}."
            )
    else:
        messages.warning(request, "تم تسجيل حالة لهذا الطالب اليوم مسبقاً.")

    return redirect('supervisor_dashboard')


@login_required
def complete_course(request, enrollment_id):
    """إنهاء الكورس وأرشفته."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    is_authorized = request.user.is_superuser or (
        enrollment.student.supervisor and 
        enrollment.student.supervisor.user == request.user
    )

    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية.")
        return redirect('supervisor_dashboard')

    if enrollment.attendances.count() < enrollment.course.sessions_count:
        messages.error(request, "عفواً، لا يمكن إنهاء الكورس لأن الطالب لم يتم جميع الحصص المقررة بعد.")
        return redirect('supervisor_dashboard')

    enrollment.is_completed = True
    enrollment.save()
    
    messages.success(request, f"مبروك! تم إنهاء كورس {enrollment.course.name} للطالب {enrollment.student.name} وتمت أرشفته.")
    return redirect('supervisor_dashboard')


# ==========================================
# 2. لوحات التحكم (مشرف، مدير، بروفايل)
# ==========================================

@never_cache
@login_required
def supervisor_dashboard(request):
    """لوحة تحكم المشرفين لمتابعة الطلاب."""
    current_user = request.user
    
    if current_user.is_superuser:
        students_queryset = Student.objects.all()
    elif hasattr(current_user, 'supervisor_profile'):
        students_queryset = Student.objects.filter(supervisor=current_user.supervisor_profile)
    else:
        messages.error(request, "غير مصرح لك بدخول لوحة المشرفين.")
        return redirect('chat_home')

    active_enrollments = Enrollment.objects.filter(is_completed=False)

    # استخدام select_related و prefetch_related لتحسين الأداء
    students = students_queryset.distinct()\
        .select_related('country', 'education_type', 'academic_year')\
        .prefetch_related(
            Prefetch('enrollment_set', queryset=active_enrollments),
            'teachers'
        )

    context = {
        'students': students,
        'is_superuser': request.user.is_superuser
    }
    return render(request, 'core/supervisor_dashboard.html', context)


@login_required(login_url='plogin') 
def profile_view(request):
    """الصفحة الشخصية للمستخدم (طالب، معلم، أو مستخدم عام)."""
    user = request.user
    
    # 1. تغيير البيانات
    password_form = PasswordChangeForm(user, request.POST or None)
    
    if request.method == 'POST':
        # تغيير اسم المستخدم
        new_username = request.POST.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, "اسم المستخدم هذا مستخدم بالفعل.")
            else:
                user.username = new_username
                user.save()
                messages.success(request, "تم تغيير اسم المستخدم بنجاح.")

        # تغيير كلمة المرور
        if 'old_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "تم تغيير كلمة المرور بنجاح.")
            else:
                messages.error(request, "يرجى تصحيح الأخطاء في نموذج كلمة المرور.")

    context = {
        'password_form': password_form,
        'notifications': Notification.objects.filter(recipient=user).order_by('-created_at')[:10],
        'is_student': False,
        'is_teacher': False,
    }

    # 2. منطق الطالب
    if hasattr(user, 'student_profile'):
        context['is_student'] = True
        student = user.student_profile
        
        enrollments = Enrollment.objects.filter(student=student, is_completed=False)
        courses_data = []
        for enroll in enrollments:
            total_sessions = enroll.course.sessions_count
            attended = Attendance.objects.filter(enrollment=enroll, status='present').count()
            percent = int((attended / total_sessions * 100)) if total_sessions > 0 else 0
            
            courses_data.append({
                'course_id': enroll.course.id, 
                'course': enroll.course.name,
                'attended': attended,
                'total': total_sessions,
                'percent': percent,
                'color': 'green' if percent >= 75 else 'red'
            })
        context['courses_data'] = courses_data

    # 3. منطق المعلم
    elif hasattr(user, 'teacher_profile'):
        context['is_teacher'] = True
        teacher = user.teacher_profile
        
        my_students = Student.objects.filter(teachers=teacher).distinct()
        
        # عرض الكورسات التي تقع ضمن اختصاص المعلم
        teacher_subjects = teacher.subjects.all()
        teacher_courses = Course.objects.filter(subject__in=teacher_subjects).distinct()
        context['teacher_courses'] = teacher_courses
        
        students_with_grades = []
        for std in my_students:
            attempts = []
            if QuizAttempt:
                attempts = QuizAttempt.objects.filter(student=std).select_related('quiz')
            
            students_with_grades.append({
                'student': std,
                'attempts': attempts
            })
            
        context['students_with_grades'] = students_with_grades

    return render(request, 'core/profile.html', context)


# ==========================================
# 3. لوحة الإدارة وتسجيل الطلاب
# ==========================================

@login_required(login_url='management_login') 
def admin_panel(req):
    """لوحة الإدارة الرئيسية: إحصائيات، بحث، وإضافة طلاب."""
    is_authorized = req.user.is_superuser or hasattr(req.user, 'manager_profile')
    
    if not is_authorized:
        messages.error(req, "عفواً، هذه الصفحة مخصصة للمديرين الإداريين فقط.")
        return redirect('chat_home')

    stats = {
        'students_count': Student.objects.count(),
        'teachers_count': Teacher.objects.count(),
        'courses_count': Course.objects.count(),
        'active_enrollments': Enrollment.objects.filter(is_completed=False).count(),
    }

    search_results = None
    student_form = StudentForm(req.POST or None)

    # منطق البحث
    query = req.GET.get('q')
    if query:
        search_results = Student.objects.filter(
            Q(name__icontains=query) |
            Q(parent_name__icontains=query) |
            Q(parent_phone__icontains=query) |
            Q(parent_email__icontains=query)
        ).only('name', 'id')

    # منطق إضافة الطالب
    if req.method == 'POST' and 'add_student' in req.POST:
        if student_form.is_valid():
            try:
                parent_email = student_form.cleaned_data.get('parent_email')
                
                # --- [بداية التعديل] ---
                # تنظيف رقم الهاتف من المسافات والعلامات لضمان اسم مستخدم صحيح
                raw_phone = student_form.cleaned_data['parent_phone']
                clean_username = raw_phone.replace(" ", "").replace("-", "").strip()
                # -----------------------

                # توليد كلمة مرور قوية
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for i in range(10)) 

                # استخدام الاسم المنظف
                username = clean_username
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{secrets.randbelow(1000)}"

                # إنشاء المستخدم
                user = User.objects.create_user(username=username, password=password)
                full_name = student_form.cleaned_data['name'].split()
                if full_name:
                    user.first_name = full_name[0]
                    if len(full_name) > 1:
                        user.last_name = full_name[-1]
                
                if parent_email:
                    user.email = parent_email
                user.save()

                # حفظ الطالب
                student = student_form.save(commit=False)
                student.user = user  
                student.save() # هذا السطر سيقوم بتفعيل إشعار المشرف تلقائياً عبر Signals
                
                # إرسال الإيميل
                if parent_email:
                    subject = 'بيانات الدخول لمنصة VexaLearn'
                    site_url = f"{req.scheme}://{req.get_host()}"
                    
                    message = f"""
                    مرحباً ولي أمر الطالب/ة {student.name}،
                    
                    تم تسجيل حساب الطالب بنجاح في المنصة.
                    
                    بيانات الدخول:
                    اسم المستخدم: {username}
                    كلمة المرور: {password}
                    
                    رابط المنصة: {site_url}
                    
                    يرجى الاحتفاظ بهذه البيانات.
                    """
                    send_mail_async(subject, message, [parent_email])
                    messages.info(req, f"تم إرسال بيانات الدخول إلى: {parent_email}")

                # عرض كلمة المرور للمدير لنسخها في حال لم يصل الإيميل
                messages.success(req, f"تم إنشاء ملف الطالب {student.name}")
                messages.warning(req, "يرجى الآن إضافة الكورسات واختيار المعلمين لهذا الطالب.")
                return redirect('add_enrollment', student_id=student.id)
            
            except Exception as e:
                messages.error(req, f"حدث خطأ أثناء الحفظ: {e}")
        else:
            messages.error(req, "يرجى التأكد من صحة البيانات المدخلة.")

    context = {
        'search_results': search_results,
        'query': query,
        'student_form': student_form,
        'stats': stats,
    }
    return render(req, 'core/admin_panel.html', context)

@login_required
def add_enrollment(request, student_id):
    """إضافة اشتراك جديد لطالب."""
    # التحقق من الصلاحية
    if not (request.user.is_superuser or hasattr(request.user, 'manager_profile')):
         messages.error(request, "ليس لديك صلاحية لإضافة اشتراكات.")
         return redirect('chat_home')

    student = get_object_or_404(Student, id=student_id)
    form = EnrollmentForm(request.POST or None)

    # ============================================================
    # [بداية التعديل الجديد]: فلترة الكورسات حسب بيانات الطالب
    # ============================================================
    
    # 1. نحدد الكورسات التابعة لنفس دولة الطالب
    courses_qs = Course.objects.filter(country=student.country)
    
    # 2. إذا كان للطالب سنة دراسية محددة، نفلتر الكورسات لتطابقها
    # ملاحظة: نستخدم academic_years (الحقل الجديد) للبحث عما إذا كانت سنة الطالب ضمن سنوات الكورس
    if student.academic_year:
        courses_qs = courses_qs.filter(academic_years=student.academic_year).distinct()
        
    # 3. تحديث قائمة الكورسات في الفورم لتظهر النتائج المفلترة فقط
    form.fields['course'].queryset = courses_qs
    
    # ============================================================

    if request.method == 'POST':
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.save()
            
            # إضافة المعلم المختار إلى قائمة معلمي الطالب
            if enrollment.teacher:
                student.teachers.add(enrollment.teacher)

            # إرسال إيميل لولي الأمر
            if student.parent_email:
                subject = f'تم تسجيل اشتراك جديد - {student.name}'
                message = f"""
                مرحباً ولي أمر الطالب/ة {student.name}،
                
                تم تسجيل الطالب بنجاح في كورس: {enrollment.course.name}
                المعلم المسؤول: {enrollment.teacher.name if enrollment.teacher else 'لم يحدد'}
                
                تاريخ البدء: {enrollment.start_date}
                السعر: {enrollment.course.price} {enrollment.course.country.currency}
                
                نتمنى له التوفيق.
                إدارة الأكاديمية
                """
                send_mail_async(subject, message, [student.parent_email])
                messages.info(request, f"تم إرسال إشعار الاشتراك لولي الأمر 📧")

            messages.success(request, f"تم إضافة اشتراك كورس {enrollment.course.name} للطالب {student.name} ✅")
            return redirect('add_enrollment', student_id=student.id)

    return render(request, 'core/add_enrollment.html', {'form': form, 'student': student})

# ==========================================
# 4. الشات والمراسلة
# ==========================================

@login_required(login_url='chat_login')
def chat_room(request, user_id=None):
    """غرفة الدردشة الرئيسية مع إصلاح خطأ الدمج (Fix Query Error)."""
    current_user = request.user

    # التحقق من صلاحية الطالب للدخول للشات
    if hasattr(current_user, 'student_profile'):
        student = current_user.student_profile
        has_active_enrollment = Enrollment.objects.filter(
            student=student, 
            is_completed=False
        ).exists()

        if not has_active_enrollment:
            messages.warning(request, "عفواً ⛔، لا يمكنك الدخول للشات حالياً. يجب أن تكون مشتركاً في كورس نشط.")
            return redirect('profile_view')

    # بناء قائمة المستخدمين المتاحين للمراسلة
    users_list = User.objects.none()

    if current_user.is_superuser:
        users_list = User.objects.filter(is_active=True)
    elif hasattr(current_user, 'manager_profile'):
        users_list = User.objects.filter(is_active=True)
    elif hasattr(current_user, 'supervisor_profile'):
        supervisor_profile = current_user.supervisor_profile
        my_students = Student.objects.filter(supervisor=supervisor_profile)
        students_users = User.objects.filter(student_profile__in=my_students)
        teachers_of_my_students = Teacher.objects.filter(student__in=my_students).distinct()
        teachers_users = User.objects.filter(teacher_profile__in=teachers_of_my_students)
        users_list = students_users | teachers_users
    elif hasattr(current_user, 'teacher_profile'):
        teacher_profile = current_user.teacher_profile
        
        # نستخدم enrollment__teacher بناءً على رسالة الخطأ السابقة التي أوضحت أن الاسم هو enrollment
        my_students = Student.objects.filter(enrollment__teacher=teacher_profile).distinct()
        
        students_users = User.objects.filter(student_profile__in=my_students)
        
        # جلب المشرفين المرتبطين بهؤلاء الطلاب
        supervisors_of_my_students = Supervisor.objects.filter(students__in=my_students).distinct()
        supervisors_users = User.objects.filter(supervisor_profile__in=supervisors_of_my_students)
        
        users_list = students_users | supervisors_users
    elif hasattr(current_user, 'student_profile'):
        student_profile = current_user.student_profile
        teachers_ids = Enrollment.objects.filter(student=student_profile).values_list('teacher__user', flat=True)
        teachers_users = User.objects.filter(id__in=teachers_ids)
        
        supervisor_user = User.objects.none()
        if student_profile.supervisor and student_profile.supervisor.user:
            supervisor_user = User.objects.filter(id=student_profile.supervisor.user.id)
        users_list = teachers_users | supervisor_user

    if not current_user.is_superuser:
        # [تصحيح الخطأ هنا]: قمنا بإزالة .distinct() من هذا الاستعلام ليمكن دمجه
        active_admins = User.objects.filter(is_superuser=True).filter(
            Q(sent_messages__receiver=current_user) | 
            Q(received_messages__sender=current_user)
        )
        users_list = users_list | active_admins

    # استعلام واحد لجلب حالة الرسائل غير المقروءة لكل المستخدمين
    unread_subquery = Message.objects.filter(
        sender=OuterRef('pk'), 
        receiver=current_user, 
        is_read=False
    )

    # تطبيق distinct() هنا في النهاية فقط
    users_list = users_list.exclude(id=current_user.id)\
        .annotate(has_unread_messages=Exists(unread_subquery))\
        .distinct()

    final_users_list = []
    for u in users_list:
        u.display_name = u.first_name + " " + u.last_name if u.first_name else u.username
        u.role_label = 'مستخدم'
        u.role_icon = 'fas fa-user'

        if hasattr(u, 'manager_profile'):
            u.display_name = u.manager_profile.name
            u.role_label = 'مدير إداري'
            u.role_icon = 'fas fa-user-tie'
        elif hasattr(u, 'supervisor_profile'):
            u.display_name = u.supervisor_profile.name
            u.role_label = 'مشرف'
            u.role_icon = 'fas fa-user-shield'
        elif hasattr(u, 'teacher_profile'):
            u.display_name = u.teacher_profile.name
            u.role_label = 'معلم'
            u.role_icon = 'fas fa-chalkboard-teacher'
        elif hasattr(u, 'student_profile'):
            u.display_name = u.student_profile.name
            u.role_label = 'طالب'
            u.role_icon = 'fas fa-user-graduate'
        elif u.is_superuser:
            u.role_label = 'Admin'
            u.role_icon = 'fas fa-cogs'
        
        u.has_unread = getattr(u, 'has_unread_messages', False)
        final_users_list.append(u)
    
    users_list = final_users_list 

    selected_user = None
    messages_list = []
    report_form = None
    already_reported_today = False
    target_student_id = None

    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        
        selected_user.display_name = selected_user.username
        selected_user.role_label = 'مستخدم'
        if hasattr(selected_user, 'manager_profile'):
            selected_user.display_name = selected_user.manager_profile.name
        elif hasattr(selected_user, 'supervisor_profile'):
            selected_user.display_name = selected_user.supervisor_profile.name
        elif hasattr(selected_user, 'teacher_profile'):
            selected_user.display_name = selected_user.teacher_profile.name
        elif hasattr(selected_user, 'student_profile'):
            selected_user.display_name = selected_user.student_profile.name
        elif selected_user.is_superuser:
            selected_user.display_name = "Admin"

        if hasattr(current_user, 'teacher_profile') and hasattr(selected_user, 'student_profile'):
            target_student = selected_user.student_profile
            target_student_id = target_student.id
            today = timezone.now().date()
            already_reported_today = DailyReport.objects.filter(
                teacher=current_user.teacher_profile,
                student=target_student,
                date=today
            ).exists()
            report_form = DailyReportForm()

        Message.objects.filter(sender=selected_user, receiver=current_user, is_read=False).update(is_read=True)

        messages_list = Message.objects.filter(
            Q(sender=current_user, receiver=selected_user) |
            Q(sender=selected_user, receiver=current_user)
        ).order_by('timestamp')

        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                Message.objects.create(sender=current_user, receiver=selected_user, content=content)
                return redirect('chat_room', user_id=user_id)

    context = {
        'users_list': users_list,
        'selected_user': selected_user,
        'chat_messages': messages_list,
        'current_user': current_user,
        'report_form': report_form,
        'already_reported_today': already_reported_today,
        'target_student_id': target_student_id,
    }
    return render(request, 'core/chat.html', context)


@login_required
def check_new_messages(request):
    """API للتحقق من الرسائل الجديدة دون تحديث الصفحة."""
    latest_message = Message.objects.filter(
        receiver=request.user, 
        is_read=False
    ).order_by('-timestamp').first()

    if latest_message:
        return JsonResponse({
            'has_new': True,
            'sender': latest_message.sender.first_name or latest_message.sender.username,
            'content': latest_message.content[:50],
            'msg_id': latest_message.id
        })
    else:
        return JsonResponse({'has_new': False})


@login_required
def submit_daily_report(request, student_id):
    """رفع التقرير اليومي للطالب من قبل المعلم."""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "عفواً، هذه الميزة للمعلمين فقط.")
        return redirect('chat_home')

    student = get_object_or_404(Student, id=student_id)
    teacher = request.user.teacher_profile
    today = timezone.now().date()

    if DailyReport.objects.filter(student=student, teacher=teacher, date=today).exists():
        messages.warning(request, "لقد قمت برفع تقرير لهذا الطالب اليوم بالفعل.")
        return redirect('chat_room', user_id=student.user.id)

    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = student
            report.teacher = teacher
            report.save()
            messages.success(request, "تم رفع التقرير اليومي بنجاح ✅")
            return redirect('chat_room', user_id=student.user.id)
    
    return redirect('chat_room', user_id=student.user.id)


# ==========================================
# 5. مكتبة المواد العلمية
# ==========================================

@login_required
def upload_material(request):
    """رفع الملفات التعليمية من قبل المعلم."""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "هذه الصفحة للمعلمين فقط.")
        return redirect('profile_view')

    teacher = request.user.teacher_profile
    
    if request.method == 'POST':
        form = MaterialForm(teacher, request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.teacher = teacher
            material.save()
            messages.success(request, f"تم رفع الملف '{material.title}' بنجاح ✅")
            return redirect('profile_view')
    else:
        form = MaterialForm(teacher)

    return render(request, 'core/upload_material.html', {'form': form})


@login_required
def course_materials(request, course_id):
    """عرض المواد التعليمية للكورس."""
    course = get_object_or_404(Course, id=course_id)
    
    # التحقق: هل الطالب مشترك؟
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        
        enrollment = Enrollment.objects.filter(student=student, course=course).first()
        
        if not enrollment:
            messages.error(request, "أنت غير مشترك في هذا الكورس.")
            return redirect('profile_view')
        
        my_teacher = enrollment.teacher
        
        if not my_teacher:
            materials = []
            messages.warning(request, "لم يتم تحديد معلم لك في هذا الكورس بعد.")
        else:
            materials = CourseMaterial.objects.filter(
                course=course, 
                teacher=my_teacher
            ).order_by('-created_at')
            
    # للمدير والمشرف
    elif request.user.is_superuser or hasattr(request.user, 'manager_profile'):
        materials = CourseMaterial.objects.filter(course=course).order_by('-created_at')
        my_teacher = None
    else:
        return redirect('profile_view')

    return render(request, 'core/course_materials.html', {
        'course': course, 
        'materials': materials,
        'teacher': my_teacher
    })


# ==========================================
# 6. صفحات الدخول والصفحات العامة
# ==========================================

def management_login(request):
    """تسجيل دخول الإداريين فقط."""
    if request.user.is_authenticated:
        if request.user.is_superuser or hasattr(request.user, 'manager_profile'):
            return redirect('admin_panel')
        else:
            return redirect('chat_logout') 

    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser or hasattr(user, 'manager_profile'):
                auth_login(request, user)
                return redirect('admin_panel')
            else:
                messages.error(request, "عفواً، غير مصرح لك بدخول لوحة الإدارة.")
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة.")

    return render(request, 'core/management_login.html', {'form': form})


def public_login(request):
    """تسجيل دخول عام (طلاب، معلمين، أولياء أمور)."""
    if request.user.is_authenticated:
        return redirect('profile_view')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            has_role = (
                user.is_superuser or 
                hasattr(user, 'student_profile') or 
                hasattr(user, 'teacher_profile') or 
                hasattr(user, 'manager_profile') or 
                hasattr(user, 'supervisor_profile')
            )

            if not has_role:
                 messages.error(request, "هذا الحساب غير نشط أو لا يملك صلاحية.")
                 return redirect('plogin')

            auth_login(request, user)
            
            if user.is_superuser:
                return redirect('admin_panel')
            else:
                return redirect('profile_view')
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
    else:
        form = AuthenticationForm()

    return render(request, 'core/public_login.html', {'form': form})


def landing_page(request):
    """الصفحة الرئيسية للموقع."""
    countries = Country.objects.all()
    selected_country_id = request.GET.get('country')
    
    if selected_country_id:
        academies = Academy.objects.filter(courses__country__id=selected_country_id).distinct()
    else:
        academies = Academy.objects.all()

    context = {
        'academies': academies,
        'countries': countries,
        'selected_country_id': int(selected_country_id) if selected_country_id else None,
        'academies_count': Academy.objects.count(),
        'courses_count': Course.objects.count(),
        'students_count': Student.objects.count(),
    }
    return render(request, 'core/landing_page.html', context)


def academy_details(request, academy_id):
    """صفحة تفاصيل الأكاديمية والكورسات."""
    academy = get_object_or_404(Academy, id=academy_id)
    courses = Course.objects.filter(academy=academy)
    
    selected_country_id = request.GET.get('country')
    if selected_country_id:
        courses = courses.filter(country__id=selected_country_id)
        
    available_country_ids = Course.objects.filter(academy=academy).values_list('country', flat=True).distinct()
    countries = Country.objects.filter(id__in=available_country_ids)
    
    return render(request, 'core/academy_details.html', {
        'academy': academy,
        'courses': courses,
        'countries': countries,
        'selected_country_id': int(selected_country_id) if selected_country_id else None,
    })


def games_page(request):
    return render(request, 'core/games_page.html')


# ==========================================
# 7. وظائف المراقبة والفيديو
# ==========================================

@login_required
def monitor_student_chat(request, student_id):
    """مراقبة شات الطالب (للمشرفين والمدراء)."""
    student = get_object_or_404(Student, id=student_id)
    
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
    elif hasattr(request.user, 'supervisor_profile') and student.supervisor == request.user.supervisor_profile:
        is_authorized = True
    elif hasattr(request.user, 'manager_profile'):
        is_authorized = True
        
    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية للاطلاع على بيانات هذا الطالب.")
        return redirect('supervisor_dashboard')

    teachers = student.teachers.all()
    supervisor = student.supervisor
    
    selected_teacher = None
    selected_supervisor = None 
    chat_messages = []

    teacher_id = request.GET.get('teacher_id')
    supervisor_id = request.GET.get('supervisor_id')

    if teacher_id:
        selected_teacher = get_object_or_404(Teacher, id=teacher_id)
        if student.user and selected_teacher.user:
            chat_messages = Message.objects.filter(
                (Q(sender=student.user, receiver=selected_teacher.user) |
                 Q(sender=selected_teacher.user, receiver=student.user))
            ).order_by('timestamp')
            
    elif supervisor_id and supervisor:
        if int(supervisor_id) == supervisor.id:
            selected_supervisor = supervisor
            if student.user and selected_supervisor.user:
                chat_messages = Message.objects.filter(
                    (Q(sender=student.user, receiver=selected_supervisor.user) |
                     Q(sender=selected_supervisor.user, receiver=student.user))
                ).order_by('timestamp')

    student_reports = DailyReport.objects.filter(student=student).select_related('teacher').order_by('-date')

    context = {
        'student': student,
        'teachers': teachers,
        'supervisor': supervisor,
        'selected_teacher': selected_teacher,
        'selected_supervisor': selected_supervisor,
        'chat_messages': chat_messages,
        'student_reports': student_reports,
    }
    return render(request, 'core/monitor_chat.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def student_full_chat_log(request, student_id):
    """سجل المحادثات الكامل للطالب (للمدير العام)."""
    student = get_object_or_404(Student, id=student_id)
    teachers = student.teachers.all()
    student_reports = DailyReport.objects.filter(student=student).order_by('-date')

    selected_teacher = None
    chat_messages = []

    teacher_id = request.GET.get('teacher_id')
    
    if teacher_id:
        try:
            selected_teacher = Teacher.objects.get(id=teacher_id)
            if student.user and selected_teacher.user:
                chat_messages = Message.objects.filter(
                    Q(sender=student.user, receiver=selected_teacher.user) | 
                    Q(sender=selected_teacher.user, receiver=student.user)
                ).order_by('timestamp')
        except Teacher.DoesNotExist:
            selected_teacher = None

    context = {
        'student': student,
        'teachers': teachers,
        'student_reports': student_reports,
        'selected_teacher': selected_teacher,
        'chat_messages': chat_messages,
    }
    
    return render(request, 'core/student_full_chat_log.html', context)


def superuser_custom_login(request):
    """تسجيل دخول مخصص للمدير العام."""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('universal_chat_monitor')
    
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                auth_login(request, user)
                return redirect('universal_chat_monitor')
            else:
                messages.error(request, "عفواً، هذه الصفحة مخصصة للمدير العام فقط.")
    
    return render(request, 'core/superuser_login.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='superuser_custom_login')
def universal_chat_monitor(request):
    """مراقبة شاملة لكل المحادثات في النظام (God Mode)."""
    all_users = User.objects.filter(is_active=True).select_related(
        'student_profile', 'teacher_profile', 'supervisor_profile', 'manager_profile'
    )
    
    users_data = []
    for u in all_users:
        role = "مستخدم"
        name = u.username 
        if hasattr(u, 'student_profile'):
            role = "طالب"
            name = u.student_profile.name
        elif hasattr(u, 'teacher_profile'):
            role = "معلم"
            name = u.teacher_profile.name
        elif hasattr(u, 'supervisor_profile'):
            role = "مشرف"
            name = u.supervisor_profile.name
        elif hasattr(u, 'manager_profile'):
            role = "مدير"
            name = u.manager_profile.name
        elif u.is_superuser:
            role = "Admin"
            
        users_data.append({
            'id': u.id,
            'name': name,
            'role': role,
            'username': u.username
        })
    
    users_data.sort(key=lambda x: x['name'])

    user1_id = request.GET.get('user1')
    user2_id = request.GET.get('user2')
    
    chat_messages = []
    daily_reports = []
    show_reports_panel = False
    
    user1_obj = None
    user2_obj = None

    if user1_id and user2_id:
        try:
            user1_obj = User.objects.get(id=user1_id)
            user2_obj = User.objects.get(id=user2_id)
            
            chat_messages = Message.objects.filter(
                (Q(sender=user1_obj, receiver=user2_obj) | 
                 Q(sender=user2_obj, receiver=user1_obj))
            ).order_by('timestamp')

            student_profile = None
            teacher_profile = None

            if hasattr(user1_obj, 'student_profile') and hasattr(user2_obj, 'teacher_profile'):
                student_profile = user1_obj.student_profile
                teacher_profile = user2_obj.teacher_profile
            
            elif hasattr(user1_obj, 'teacher_profile') and hasattr(user2_obj, 'student_profile'):
                teacher_profile = user1_obj.teacher_profile
                student_profile = user2_obj.student_profile

            if student_profile and teacher_profile:
                show_reports_panel = True
                daily_reports = DailyReport.objects.filter(
                    student=student_profile,
                    teacher=teacher_profile
                ).order_by('-date')

        except User.DoesNotExist:
            pass

    context = {
        'users_data': users_data,
        'chat_messages': chat_messages,
        'daily_reports': daily_reports,
        'show_reports_panel': show_reports_panel,
        'user1_id': int(user1_id) if user1_id else None,
        'user2_id': int(user2_id) if user2_id else None,
        'user1_obj': user1_obj,
        'user2_obj': user2_obj,
    }
    return render(request, 'core/universal_chat_monitor.html', context)


@login_required
def video_call_view(request, room_name):
    """إنشاء وإدارة جلسة الفيديو باستخدام Agora."""
    APP_ID = settings.AGORA_APP_ID
    APP_CERTIFICATE = settings.AGORA_APP_CERTIFICATE

    if not APP_ID or not APP_CERTIFICATE:
        messages.error(request, "إعدادات الفيديو غير مكتملة في السيرفر.")
        return redirect('chat_home')

    uid = request.user.id 
    expiration_time_in_seconds = 3600 * 24 
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    role = 1 

    try:
        token = RtcTokenBuilder.buildTokenWithUid(
            APP_ID, 
            APP_CERTIFICATE, 
            room_name, 
            uid, 
            role, 
            privilege_expired_ts
        )
    except Exception as e:
        print(f"Error generating token: {e}")
        messages.error(request, "حدث خطأ أثناء إنشاء جلسة الفيديو.")
        return redirect('chat_home')

    context = {
        'room_name': room_name,
        'app_id': APP_ID,
        'token': token,
        'uid': uid,
        'user_name': request.user.first_name or request.user.username,
    }
    return render(request, 'core/video_call.html', context)


def load_teachers(request):
    """API لفلترة المعلمين حسب الكورس المختار (AJAX)."""
    course_id = request.GET.get('course_id')
    teachers = Teacher.objects.none()
    
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            if course.subject:
                teachers = course.subject.teachers.all()
        except:
            pass
            
    return render(request, 'core/teacher_dropdown_list_options.html', {'teachers': teachers})


def load_education_types(request):
    country_id = request.GET.get('country_id')
    if country_id:
        types = EducationType.objects.filter(country_id=country_id).values('id', 'name')
        return JsonResponse(list(types), safe=False)
    return JsonResponse([], safe=False)

def load_academic_years(request):
    country_id = request.GET.get('country_id')
    if country_id:
        years = AcademicYear.objects.filter(country_id=country_id).values('id', 'name')
        return JsonResponse(list(years), safe=False)
    return JsonResponse([], safe=False)
=======
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Prefetch
from .models import Student, Enrollment, Attendance
from django.views.decorators.cache import never_cache

# 1. دالة تسجيل الحضور (مع منع الزيادة عن العدد المقرر)
@login_required
def mark_attendance(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # التحقق من صلاحية المشرف
    if enrollment.student.supervisor != request.user:
        messages.error(request, "ليس لديك صلاحية لتسجيل حضور لهذا الطالب.")
        return redirect('supervisor_dashboard')

    # التحقق من اكتمال عدد الحصص
    current_count = enrollment.attendances.count()
    total_sessions = enrollment.course.sessions_count

    if current_count >= total_sessions:
        messages.error(request, f"عفواً، لقد اكتمل عدد حصص هذا الكورس ({total_sessions} حصة).")
        return redirect('supervisor_dashboard')

    # تسجيل الحضور
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        enrollment=enrollment, 
        date=today
    )

    if created:
        messages.success(request, f"تم تسجيل حضور {enrollment.student.name} بنجاح.")
    else:
        messages.warning(request, "تم تسجيل الحضور لهذا الطالب اليوم مسبقاً.")

    return redirect('supervisor_dashboard')


# 2. دالة إنهاء الكورس (زر Done) - هذه هي الدالة التي كانت ناقصة
@login_required
def complete_course(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # 1. التحقق من الصلاحية
    if enrollment.student.supervisor != request.user:
        messages.error(request, "ليس لديك صلاحية.")
        return redirect('supervisor_dashboard')

    # --- (جديد) 2. التحقق من اكتمال الحصص قبل الإنهاء ---
    if enrollment.attendances.count() < enrollment.course.sessions_count:
        messages.error(request, "عفواً، لا يمكن إنهاء الكورس لأن الطالب لم يتم جميع الحصص المقررة بعد.")
        return redirect('supervisor_dashboard')
    # ----------------------------------------------------

    # 3. تحويل الكورس إلى مكتمل
    enrollment.is_completed = True
    enrollment.save()
    
    messages.success(request, f"مبروك! تم إنهاء كورس {enrollment.course.name} للطالب {enrollment.student.name} وتمت أرشفته.")
    return redirect('supervisor_dashboard')


# 3. دالة لوحة المشرف (محدثة لإخفاء الكورسات المنتهية)
@never_cache
@login_required
def supervisor_dashboard(request):
    current_user = request.user
    
    # 1. تعريف الكورسات النشطة فقط (غير المكتملة)
    active_enrollments = Enrollment.objects.filter(is_completed=False)

    # 2. جلب "كل" الطلاب المرتبطين بالمشرف (أزلنا شرط أن يكون لديه كورس)
    students = Student.objects.filter(supervisor=current_user).distinct()\
        .select_related('country', 'education_type', 'academic_year')\
        .prefetch_related(
            # نجلب للطالب كورساته النشطة فقط لعرضها
            Prefetch('enrollment_set', queryset=active_enrollments),
            'teachers'
        )

    context = {
        'students': students
    }
    return render(request, 'core/supervisor_dashboard.html', context)
>>>>>>> d5830918c0c5f5125220644ff97bb92f7726c7f7
