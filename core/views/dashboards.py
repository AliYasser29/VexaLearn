from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from core.models import Student, Enrollment
from core.utils import is_active_manager, is_active_supervisor

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

    # استخدام الـ Manager المخصص لتبسيط الاستعلام وتخفيف الضغط
    students = students_queryset.active_with_relations().distinct().prefetch_related(
        Prefetch('enrollment_set', queryset=active_enrollments)
    )

    # جلب إحصائيات التقييمات والاختبارات لكل طالب بكفاءة عالية (Zero N+1 queries)
    from quiz.models import Quiz, QuizAttempt
    
    if QuizAttempt and Quiz:
        # 1. جلب كافة المحاولات للطلاب المعروضين
        student_ids = [student.id for student in students]
        attempts = QuizAttempt.objects.filter(student_id__in=student_ids).select_related('quiz', 'quiz__course').prefetch_related('quiz__questions')
        
        from collections import defaultdict
        attempts_by_student = defaultdict(list)
        for attempt in attempts:
            attempts_by_student[attempt.student_id].append(attempt)
            
        # 2. جلب كافة الكورسات المسجلين بها
        enrolled_course_ids = set()
        for student in students:
            for enroll in student.enrollment_set.all():
                enrolled_course_ids.add(enroll.course_id)
                
        # 3. جلب جميع الاختبارات المرتبطة بهذه الكورسات
        quizzes = Quiz.objects.filter(course_id__in=list(enrolled_course_ids)).prefetch_related('specific_students', 'questions')
        
        # خارطة للطلاب المحددين لكل اختبار لتسريع التحقق في الذاكرة
        quiz_specific_students = {}
        for quiz in quizzes:
            if quiz.specific_students.exists():
                quiz_specific_students[quiz.id] = set(quiz.specific_students.values_list('id', flat=True))
            else:
                quiz_specific_students[quiz.id] = None
                
        # 4. ربط الاختبارات والنتائج بكل طالب
        for student in students:
            student_attempts = attempts_by_student[student.id]
            attempted_quiz_ids = {a.quiz_id for a in student_attempts}
            student_courses = {e.course_id for e in student.enrollment_set.all()}
            
            student_unsolved = []
            for quiz in quizzes:
                if quiz.course_id in student_courses:
                    spec_studs = quiz_specific_students[quiz.id]
                    if spec_studs is None or student.id in spec_studs:
                        if quiz.id not in attempted_quiz_ids:
                            student_unsolved.append(quiz)
                            
            student.taken_attempts = student_attempts
            student.unsolved_quizzes = student_unsolved
    else:
        for student in students:
            student.taken_attempts = []
            student.unsolved_quizzes = []

    context = {
        'students': students,
        'is_superuser': request.user.is_superuser
    }
    return render(request, 'core/supervisor_dashboard.html', context)

@login_required
def student_directory(request):
    # Fetch active students with related data to avoid N+1 queries using our manager
    students = Student.objects.active_with_relations()
    return render(request, 'core/student_directory.html', {'students': students})

@login_required
def student_dashboard(request):
    return redirect('profile_view')

@login_required
def instructor_dashboard(request):
    return redirect('profile_view')
