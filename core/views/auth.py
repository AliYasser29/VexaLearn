from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from core.models import Notification, Enrollment, Attendance, CourseMaterial, Student, Course
from core.utils import is_active_student, is_active_teacher, is_active_supervisor, is_active_manager

try:
    from quiz.models import Quiz, QuizAttempt
except ImportError:
    Quiz = None
    QuizAttempt = None

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
        
    return redirect(get_dashboard_url_for_user(request.user))

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

        # جلب الاختبارات والاختبارات غير المحلولة للطالب
        from django.db.models import Q
        
        taken_attempts = QuizAttempt.objects.filter(student=student).select_related('quiz', 'quiz__course').prefetch_related('quiz__questions').order_by('-completed_at')
        
        enrolled_courses = [e.course for e in enrollments]
        all_available_quizzes = Quiz.objects.filter(course__in=enrolled_courses).filter(
            Q(specific_students__isnull=True) | Q(specific_students=student)
        ).distinct().select_related('course').prefetch_related('questions')
        
        attempted_quiz_ids = taken_attempts.values_list('quiz_id', flat=True)
        unsolved_quizzes = all_available_quizzes.exclude(id__in=attempted_quiz_ids).order_by('-created_at')
        
        context['taken_attempts'] = taken_attempts
        context['unsolved_quizzes'] = unsolved_quizzes

    # 3. منطق المعلم
    elif hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
        
        # جلب قائمة طلاب المعلم النشطين حالياً وتفاصيلهم
        active_students_data = []
        teacher_enrollments = Enrollment.objects.filter(teacher=teacher, is_completed=False).select_related(
            'student', 'student__academic_year', 'student__country', 'course', 'course__academy'
        )
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
                'academic_year': student.academic_year.name if student.academic_year else 'غير محدد',
                'country': student.country.name if student.country else 'غير محدد',
                'academy': enroll.course.academy.name if enroll.course.academy else 'منصة فيكسا',
                'attempts': attempts
            })
        context['active_students_data'] = active_students_data
        
        # جلب الكورسات النشطة التي يدرسها المعلم
        teacher_courses = Course.objects.filter(subject__in=teacher.subjects.all()).distinct().select_related('subject', 'country')
        context['teacher_courses'] = teacher_courses

        # جلب الاختبارات المعلقة بانتظار تصحيح المعلم
        if QuizAttempt:
            teacher_student_ids = teacher_enrollments.values_list('student_id', flat=True).distinct()
            teacher_course_ids = teacher_enrollments.values_list('course_id', flat=True).distinct()
            
            pending_grade_attempts = QuizAttempt.objects.filter(
                student_id__in=teacher_student_ids,
                quiz__course_id__in=teacher_course_ids,
                status='pending'
            ).select_related('student', 'quiz', 'quiz__course').order_by('-completed_at')
            context['pending_grade_attempts'] = pending_grade_attempts

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
