from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Course, Enrollment
from .models import Quiz, Question, Choice, QuizAttempt
from .forms import QuizForm, QuestionForm, ChoiceFormSet

# --- دوال التحقق من الصلاحيات ---

def is_teacher_or_superuser(user):
    return user.is_superuser or hasattr(user, 'teacher_profile')

def is_student_or_superuser(user):
    return user.is_superuser or hasattr(user, 'student_profile')

# --------------------------------

# 1. صفحة إنشاء اختبار (للمعلم أو المدير فقط)
@login_required
@user_passes_test(is_teacher_or_superuser)
def create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # حماية إضافية: إذا كان معلماً، هل هذا الكورس يخصه؟
    if not request.user.is_superuser:
        # نفترض أن المعلم مرتبط بالكورس عبر الطلاب أو علاقة مباشرة (حسب هيكلة الموديل لديك)
        # هنا سنفترض أن المعلم لديه صلاحية طالما هو معلم (للتبسيط)
        # أو يمكنك إضافة شرط: if course not in request.user.teacher_profile.courses.all(): ...
        pass

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, f"تم إنشاء الاختبار '{quiz.title}' بنجاح. الآن أضف الأسئلة.")
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'quiz/create_quiz.html', {'form': form, 'course': course})


@login_required
@user_passes_test(is_teacher_or_superuser)
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            # Save the related choices
            choices = formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
            
            messages.success(request, "تم إضافة السؤال بنجاح.")
            
            if 'save_and_add_another' in request.POST:
                return redirect('add_question', quiz_id=quiz.id)
            else:
                return redirect('/') 
        else:
            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    messages.error(request, f"خطأ في الخيارات: {error}")
            messages.error(request, "يرجى مراجعة الأخطاء في النموذج.")
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()

    return render(request, 'quiz/add_question.html', {'form': form, 'quiz': quiz, 'formset': formset})


# 3. صفحة حل الاختبار (للطالب أو المدير فقط)
@login_required
@user_passes_test(is_student_or_superuser)
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = None

    if not request.user.is_superuser:
        student = request.user.student_profile
        
        is_enrolled = Enrollment.objects.filter(student=student, course=quiz.course).exists()
        if not is_enrolled:
            messages.error(request, "أنت غير مشترك في هذا الكورس.")
            return redirect('quiz:quiz_dashboard')

        if quiz.specific_students.exists():
            if student not in quiz.specific_students.all():
                messages.error(request, "هذا الاختبار غير مخصص لك.")
                return redirect('quiz:quiz_dashboard')

        if QuizAttempt.objects.filter(student=student, quiz=quiz).exists():
            messages.warning(request, "لقد قمت بأداء هذا الاختبار مسبقاً.")
            return redirect('quiz:quiz_dashboard')

    if request.method == 'POST':
        questions = quiz.questions.all().prefetch_related('choices')
        total_marks = sum(q.marks for q in questions)
        earned_marks = 0
        
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                try:
                    selected_choice = Choice.objects.get(id=int(selected_choice_id), question=question)
                    if selected_choice.is_correct:
                        earned_marks += question.marks
                except (ValueError, Choice.DoesNotExist):
                    pass
                    
        percentage = (earned_marks / total_marks) * 100 if total_marks > 0 else 0
        passed = percentage >= quiz.pass_score
        
        if student:
            QuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                score=percentage,
                passed=passed
            )
            messages.success(request, f"تم تسليم إجاباتك بنجاح! درجتك: {percentage:.1f}%")
        else:
            messages.info(request, f"حساب مسؤول: تم تقييم إجاباتك بنجاح! النتيجة: {percentage:.1f}% (لم يتم تسجيل محاولة للـ Admin)")
            
        return redirect('quiz:quiz_dashboard')
        
    else:
        questions = quiz.questions.all().prefetch_related('choices')
        return render(request, 'quiz/take_quiz.html', {
            'quiz': quiz,
            'questions': questions
        })


@login_required
def quiz_dashboard(request):
    """لوحة التحكم للاختبارات (عرض الاختبارات المتاحة للطلاب والمنشأة للمعلمين)."""
    user = request.user
    
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        active_enrollments = Enrollment.objects.filter(student=student, is_completed=False)
        enrolled_courses = [e.course for e in active_enrollments]
        
        from django.db.models import Q
        quizzes = Quiz.objects.filter(course__in=enrolled_courses).filter(
            Q(specific_students__isnull=True) | Q(specific_students=student)
        ).distinct().select_related('course')
        
        completed_attempts = QuizAttempt.objects.filter(student=student).select_related('quiz')
        attempts_dict = {attempt.quiz_id: attempt for attempt in completed_attempts}
        
        for quiz in quizzes:
            quiz.user_attempt = attempts_dict.get(quiz.id)
            
        completed_count = sum(1 for q in quizzes if q.user_attempt is not None)
        pending_count = sum(1 for q in quizzes if q.user_attempt is None)
        
        context = {
            'role': 'student',
            'quizzes': quizzes,
            'completed_count': completed_count,
            'pending_count': pending_count,
        }
        
    elif hasattr(user, 'teacher_profile') or user.is_superuser:
        courses = Course.objects.all()
        if hasattr(user, 'teacher_profile'):
            teacher_profile = user.teacher_profile
            courses_via_enrollment = Course.objects.filter(enrollment__teacher=teacher_profile)
            courses_via_subject = Course.objects.filter(subject__in=teacher_profile.subjects.all())
            courses = (courses_via_enrollment | courses_via_subject).distinct()
            
        quizzes = Quiz.objects.filter(course__in=courses).distinct().select_related('course')
        
        context = {
            'role': 'teacher',
            'courses': courses,
            'quizzes': quizzes,
        }
    else:
        context = {
            'role': 'other',
            'quizzes': [],
        }
        
    return render(request, 'quiz/quiz_dashboard.html', context)