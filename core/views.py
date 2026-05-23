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
from core.tasks import send_email_task

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

from core.utils import is_active_manager, is_active_supervisor, is_active_teacher, is_active_student

@never_cache
@login_required(login_url='login')
def supervisor_dashboard(request):
    """لوحة تحكم المشرفين لمتابعة الطلاب."""
    if is_active_manager(request):
        students_queryset = Student.objects.all()
    elif is_active_supervisor(request):
        students_queryset = Student.objects.filter(supervisor=request.user.supervisor_profile)
    else:
        messages.error(request, "غير مصرح لك بدخول لوحة المشرفين بهذا الدور.")
        return redirect('chat_home')


    active_enrollments = Enrollment.objects.filter(is_completed=False).select_related('course').prefetch_related('attendances')

    students = students_queryset.distinct()\
        .select_related('country', 'education_type', 'academic_year')\
        .prefetch_related(
            Prefetch('enrollment_set', queryset=active_enrollments),
            'teachers',
            'daily_reports__teacher'
        )

    context = {
        'students': students,
        'is_superuser': request.user.is_superuser
    }
    return render(request, 'core/supervisor_dashboard.html', context)


@login_required(login_url='login') 
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
    }

    # 2. منطق الطالب
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        
        enrollments = Enrollment.objects.filter(student=student, is_completed=False).select_related('course', 'teacher')
        courses_data = []
        for enroll in enrollments:
            total_sessions = enroll.course.sessions_count
            attended = Attendance.objects.filter(enrollment=enroll, status='present').count()
            percent = int((attended / total_sessions * 100)) if total_sessions > 0 else 0
            
            # جلب المواد والمرفقات المرفوعة لهذا الكورس من قبل المعلم
            materials = []
            if enroll.teacher:
                materials = CourseMaterial.objects.filter(course=enroll.course, teacher=enroll.teacher).order_by('-created_at')
            else:
                materials = CourseMaterial.objects.filter(course=enroll.course).order_by('-created_at')
            
            courses_data.append({
                'course_id': enroll.course.id, 
                'course': enroll.course.name,
                'attended': attended,
                'total': total_sessions,
                'percent': percent,
                'color': 'green' if percent >= 75 else 'red',
                'teacher_name': enroll.teacher.name if enroll.teacher else 'لم يحدد بعد',
                'materials': materials
            })
        context['courses_data'] = courses_data

    # 3. منطق المعلم
    elif hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
        
        # جلب قائمة طلاب المعلم النشطين حالياً وتفاصيلهم
        active_students_data = []
        teacher_enrollments = Enrollment.objects.filter(teacher=teacher, is_completed=False).select_related('student', 'course')
        for enroll in teacher_enrollments:
            student = enroll.student
            attended = enroll.attendances.filter(status='present').count()
            total = enroll.course.sessions_count
            
            # جلب محاولات الاختبارات المسلمة لهذا الكورس
            attempts = []
            if QuizAttempt:
                attempts = QuizAttempt.objects.filter(student=student, quiz__course=enroll.course).select_related('quiz')
                
            active_students_data.append({
                'student_name': student.name,
                'course_name': enroll.course.name,
                'attended': attended,
                'total': total,
                'phone': student.parent_phone,
                'attempts': attempts
            })
        context['active_students_data'] = active_students_data

    # 4. منطق المشرف
    elif hasattr(user, 'supervisor_profile'):
        supervisor = user.supervisor_profile
        supervisor_students = Student.objects.filter(supervisor=supervisor).select_related('academic_year', 'country')
        
        supervisor_students_data = []
        for student in supervisor_students:
            active_enrollments = Enrollment.objects.filter(student=student, is_completed=False).select_related('course')
            courses = []
            for enroll in active_enrollments:
                attended = enroll.attendances.filter(status='present').count()
                total = enroll.course.sessions_count
                percent = int((attended / total * 100)) if total > 0 else 0
                courses.append({
                    'name': enroll.course.name,
                    'attended': attended,
                    'total': total,
                    'percent': percent
                })
            supervisor_students_data.append({
                'student': student,
                'courses': courses
            })
        context['supervisor_students_data'] = supervisor_students_data

    return render(request, 'core/profile.html', context)


# ==========================================
# 3. لوحة الإدارة وتسجيل الطلاب
# ==========================================

@login_required(login_url='login') 
def admin_panel(req, student_id=None):
    """بوابة البحث والاشتراكات للطلاب المسجلين مع تسجيل طلاب جدد."""
    if not is_active_manager(req):
        messages.error(req, "عفواً، هذه الصفحة مخصصة للمديرين الإداريين فقط بهذا الدور.")
        return redirect('chat_home')

    stats = {
        'students_count': Student.objects.count(),
        'teachers_count': Teacher.objects.count(),
        'courses_count': Course.objects.count(),
        'active_enrollments': Enrollment.objects.filter(is_completed=False).count(),
    }

    # دائماً ننشئ استمارة تسجيل طالب جديدة فارغة
    student_form = StudentForm(req.POST or None)

    search_results = None
    query = req.GET.get('q', '').strip()
    if query:
        # البحث الذكي باستخدام الاسم، أو الهاتف، أو الإيميل، أو الرقم التعريفي
        q_obj = Q(name__icontains=query) | Q(parent_phone__icontains=query) | Q(parent_email__icontains=query)
        if query.isdigit():
            q_obj |= Q(id=int(query))
            
        search_results = Student.objects.filter(q_obj).select_related('country', 'education_type', 'academic_year')

    # منطق تسجيل طالب جديد فقط (لا يوجد تعديل)
    if req.method == 'POST':
        if student_form.is_valid():
            try:
                parent_email = student_form.cleaned_data.get('parent_email')
                raw_phone = student_form.cleaned_data['parent_phone']
                clean_username = raw_phone.replace(" ", "").replace("-", "").strip()

                password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10)) 
                username = clean_username
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{secrets.randbelow(1000)}"

                user = User.objects.create_user(username=username, password=password)
                full_name = student_form.cleaned_data['name'].split()
                if full_name:
                    user.first_name = full_name[0]
                    if len(full_name) > 1:
                        user.last_name = full_name[-1]
                
                if parent_email:
                    user.email = parent_email
                user.save()

                student = student_form.save(commit=False)
                student.user = user  
                student.save()
                
                if parent_email:
                    subject = 'بيانات الدخول لمنصة VexaLearn'
                    site_url = f"{req.scheme}://{req.get_host()}"
                    message = f"""
                    مرحباً ولي أمر الطالب/ة {student.name}،
                    
                    تم تسجيل حساب الطالب بنجاح في المنصة.
                    
                    بيانات الدخول:
                    اسم المستخدم: {username}
                    word: {password}
                    
                    رابط المنصة: {site_url}
                    """
                    send_email_task.delay(subject, message, [parent_email])
                    messages.info(req, f"تم إرسال بيانات الدخول إلى: {parent_email}")

                messages.success(req, f"تم إنشاء ملف الطالب {student.name} بنجاح. Credentials: {username} / {password} ✅")
                return redirect('add_enrollment', student_id=student.id)
            
            except Exception as e:
                messages.error(req, f"حدث خطأ أثناء الحفظ: {e}")
        else:
            messages.error(req, "يرجى التأكد من صحة البيانات المدخلة في استمارة التسجيل.")

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
                send_email_task.delay(subject, message, [student.parent_email])
                messages.info(request, f"تم إرسال إشعار الاشتراك لولي الأمر 📧")

            messages.success(request, f"تم إضافة اشتراك كورس {enrollment.course.name} للطالب {student.name} ✅")
            return redirect('add_enrollment', student_id=student.id)

    return render(request, 'core/add_enrollment.html', {'form': form, 'student': student})

@login_required
def switch_role(request, role_name):
    """
    يتيح للمستخدم التبديل بين أدواره المختلفة (طالب، معلم، إلخ)
    """
    # التحقق من أن الدور المطلوب هو من ضمن الأدوار المتاحة للمستخدم
    available_roles = []
    if hasattr(request.user, 'student_profile'): available_roles.append('student')
    if hasattr(request.user, 'teacher_profile'): available_roles.append('teacher')
    if hasattr(request.user, 'supervisor_profile'): available_roles.append('supervisor')
    if hasattr(request.user, 'manager_profile') or request.user.is_superuser: 
        available_roles.append('manager')
    
    if role_name in available_roles:
        request.session['active_role'] = role_name
        messages.success(request, f"تم التبديل إلى واجهة {role_name} بنجاح.")
    else:
        messages.error(request, "ليس لديك صلاحية لهذه الواجهة.")
        
    return redirect('dashboard')


# ==========================================
# 4. الشات والمراسلة
# ==========================================

@login_required(login_url='login')
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
    q_objects = Q()

    if current_user.is_superuser or hasattr(current_user, 'manager_profile'):
        q_objects = Q(is_active=True)
    elif hasattr(current_user, 'supervisor_profile'):
        supervisor_profile = current_user.supervisor_profile
        q_objects = Q(student_profile__supervisor=supervisor_profile) | \
                    Q(teacher_profile__student__supervisor=supervisor_profile)
    elif hasattr(current_user, 'teacher_profile'):
        teacher_profile = current_user.teacher_profile
        q_objects = Q(student_profile__enrollment__teacher=teacher_profile) | \
                    Q(supervisor_profile__students__enrollment__teacher=teacher_profile)
    elif hasattr(current_user, 'student_profile'):
        student_profile = current_user.student_profile
        q_objects = Q(teacher_profile__enrollment__student=student_profile) | \
                    Q(supervisor_profile__students=student_profile)

    users_list = User.objects.filter(q_objects).filter(is_active=True)

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


@user_passes_test(lambda u: u.is_superuser, login_url='login')
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

    # Authorization Check
    import re
    is_authorized = False
    
    # 1. Match VexaLearn_<user1_id>_<user2_id> format
    match = re.match(r'^VexaLearn_(\d+)_(\d+)$', room_name)
    if match:
        try:
            u1_id = int(match.group(1))
            u2_id = int(match.group(2))
            
            current_user = request.user
            if current_user.id in [u1_id, u2_id]:
                other_user_id = u2_id if current_user.id == u1_id else u1_id
                
                try:
                    other_user = User.objects.get(id=other_user_id, is_active=True)
                    
                    # A. Superuser or Manager on either side has global relationship
                    if (current_user.is_superuser or hasattr(current_user, 'manager_profile') or 
                            other_user.is_superuser or hasattr(other_user, 'manager_profile')):
                        is_authorized = True
                    else:
                        # B. Check student-teacher, student-supervisor, or teacher-supervisor relations
                        def check_student_teacher(u_student, u_teacher):
                            if hasattr(u_student, 'student_profile') and hasattr(u_teacher, 'teacher_profile'):
                                student = u_student.student_profile
                                teacher = u_teacher.teacher_profile
                                if Enrollment.objects.filter(student=student, teacher=teacher, is_completed=False).exists():
                                    return True
                                if student.teachers.filter(id=teacher.id).exists():
                                    return True
                            return False

                        def check_student_supervisor(u_student, u_supervisor):
                            if hasattr(u_student, 'student_profile') and hasattr(u_supervisor, 'supervisor_profile'):
                                student = u_student.student_profile
                                supervisor = u_supervisor.supervisor_profile
                                if student.supervisor == supervisor:
                                    return True
                            return False

                        def check_teacher_supervisor(u_teacher, u_supervisor):
                            if hasattr(u_teacher, 'teacher_profile') and hasattr(u_supervisor, 'supervisor_profile'):
                                teacher = u_teacher.teacher_profile
                                supervisor = u_supervisor.supervisor_profile
                                if Enrollment.objects.filter(teacher=teacher, student__supervisor=supervisor, is_completed=False).exists():
                                    return True
                            return False

                        if check_student_teacher(current_user, other_user) or check_student_teacher(other_user, current_user):
                            is_authorized = True
                        elif check_student_supervisor(current_user, other_user) or check_student_supervisor(other_user, current_user):
                            is_authorized = True
                        elif check_teacher_supervisor(current_user, other_user) or check_teacher_supervisor(other_user, current_user):
                            is_authorized = True
                        
                        # C. Fallback to general chat permission logic (Q objects)
                        if not is_authorized:
                            q_objects = Q()
                            if hasattr(current_user, 'supervisor_profile'):
                                supervisor_profile = current_user.supervisor_profile
                                q_objects = Q(student_profile__supervisor=supervisor_profile) | \
                                            Q(teacher_profile__student__supervisor=supervisor_profile)
                            elif hasattr(current_user, 'teacher_profile'):
                                teacher_profile = current_user.teacher_profile
                                q_objects = Q(student_profile__enrollment__teacher=teacher_profile) | \
                                            Q(supervisor_profile__students__enrollment__teacher=teacher_profile)
                            elif hasattr(current_user, 'student_profile'):
                                student_profile = current_user.student_profile
                                q_objects = Q(teacher_profile__enrollment__student=student_profile) | \
                                            Q(supervisor_profile__students=student_profile)
                            
                            if q_objects and User.objects.filter(q_objects).filter(id=other_user_id).exists():
                                is_authorized = True
                except User.DoesNotExist:
                    is_authorized = False
        except ValueError:
            is_authorized = False

    # 2. Match 'general' format
    elif room_name == 'general':
        if (request.user.is_superuser or 
                hasattr(request.user, 'manager_profile') or 
                hasattr(request.user, 'supervisor_profile') or 
                hasattr(request.user, 'teacher_profile')):
            is_authorized = True
        elif hasattr(request.user, 'student_profile'):
            if Enrollment.objects.filter(student=request.user.student_profile, is_completed=False).exists():
                is_authorized = True

    # 3. Match numeric course_id
    else:
        try:
            course_id_int = int(room_name)
            if request.user.is_superuser or hasattr(request.user, 'manager_profile'):
                is_authorized = True
            elif hasattr(request.user, 'teacher_profile'):
                if Enrollment.objects.filter(course_id=course_id_int, teacher=request.user.teacher_profile).exists():
                    is_authorized = True
            elif hasattr(request.user, 'student_profile'):
                if Enrollment.objects.filter(course_id=course_id_int, student=request.user.student_profile, is_completed=False).exists():
                    is_authorized = True
        except ValueError:
            is_authorized = False

    if not is_authorized:
        messages.error(request, "غير مصرح لك بدخول هذه الجلسة.")
        return redirect('chat_home')

    uid = request.user.id 
    expiration_time_in_seconds = 7200 
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

@login_required
def student_directory(request):
    # Fetch active students with related data to avoid N+1 queries
    students = Student.objects.filter(is_deleted=False).select_related('academic_year', 'country', 'education_type')
    return render(request, 'core/student_directory.html', {'students': students})

# --- Unified Login System ---
from django.urls import reverse

def get_dashboard_url_for_user(user):
    """Returns the correct dashboard URL based on the user's role.
    Now redirects all users to the centralized profile view dashboard."""
    return reverse('profile_view')

def unified_login_view(request):
    """Unified login endpoint for all users."""
    if request.user.is_authenticated:
        return redirect(get_dashboard_url_for_user(request.user))
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Additional logic from public_login to verify the user has a valid role
            has_role = (
                user.is_superuser or 
                hasattr(user, 'student_profile') or 
                hasattr(user, 'teacher_profile') or 
                hasattr(user, 'manager_profile') or 
                hasattr(user, 'supervisor_profile')
            )
            
            if not has_role:
                 messages.error(request, "This account is inactive or has no valid role assigned.")
                 return redirect('login')
                 
            auth_login(request, user)
            
            # Use 'next' parameter if available, otherwise redirect to dashboard
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            return redirect(get_dashboard_url_for_user(user))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})

@login_required
def student_dashboard(request):
    return render(request, 'core/student_dashboard.html', {})

@login_required
def instructor_dashboard(request):
    return render(request, 'core/instructor_dashboard.html', {})


