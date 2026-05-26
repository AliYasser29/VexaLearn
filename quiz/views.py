from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Course, Enrollment, Student
from .models import Quiz, Question, Choice, QuizAttempt
from .forms import QuizForm, QuestionForm, ChoiceFormSet

# --- دوال التحقق من الصلاحيات ---

def is_teacher_or_superuser(user):
    return user.is_superuser or hasattr(user, 'teacher_profile')

def is_student_or_superuser(user):
    return user.is_superuser or hasattr(user, 'student_profile')

# --------------------------------

@login_required
@user_passes_test(is_teacher_or_superuser)
def create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # حماية إضافية: إذا كان معلماً، هل هذا الكورس يخصه؟
    if not request.user.is_superuser:
        teacher = request.user.teacher_profile
        # التحقق من أن مادة الكورس تقع ضمن المواد الدراسية المسندة للمعلم
        if course.subject not in teacher.subjects.all():
            messages.error(request, "غير مصرح لك بإنشاء اختبارات لهذا الكورس لأنك لا تدرس هذه المادة.")
            return redirect('quiz:quiz_dashboard')

    if request.method == 'POST':
        form = QuizForm(request.POST)
        
        # فلترة الطلاب المستهدفين في النموذج لتأمين BOLA
        if not request.user.is_superuser:
            teacher = request.user.teacher_profile
            form.fields['specific_students'].queryset = Student.objects.filter(
                enrollment__course=course,
                enrollment__teacher=teacher,
                enrollment__is_completed=False
            ).distinct()
        else:
            form.fields['specific_students'].queryset = Student.objects.filter(
                enrollment__course=course,
                enrollment__is_completed=False
            ).distinct()
            
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            form.save_m2m() # حفظ الطلاب المحددين في ManyToMany
            
            # --- تكامل نظام الرسائل (إرسال رابط الاختبار تلقائياً) ---
            from core.models import Enrollment, Message
            
            session_text = f"رقم الحصة: {quiz.session_number}" if quiz.session_number else "لكامل الكورس"
            content = (
                f"أهلاً بك! لقد قام المعلم بإعداد اختبار جديد لك:\n"
                f"📝 عنوان الاختبار: {quiz.title}\n"
                f"📚 الكورس: {course.name}\n"
                f"⏱️ المدة: {quiz.duration} دقيقة\n"
                f"🔢 {session_text}\n\n"
                f"يمكنك بدء حل الاختبار الآن بالضغط على الرابط التالي:\n"
                f"/quiz/take/{quiz.id}/"
            )
            
            if quiz.specific_students.exists():
                students_to_message = quiz.specific_students.all()
            else:
                if request.user.is_superuser:
                    enrollments = Enrollment.objects.filter(course=course, is_completed=False)
                else:
                    teacher = request.user.teacher_profile
                    enrollments = Enrollment.objects.filter(course=course, teacher=teacher, is_completed=False)
                student_ids = enrollments.values_list('student_id', flat=True).distinct()
                students_to_message = Student.objects.filter(id__in=student_ids)
                
            for student in students_to_message:
                if student.user:
                    Message.objects.create(
                        sender=request.user,
                        receiver=student.user,
                        content=content
                    )
            
            messages.success(request, f"تم إنشاء الاختبار '{quiz.title}' بنجاح وإرساله للطلاب عبر الشات. الآن أضف الأسئلة.")
            return redirect('quiz:add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
        # فلترة الطلاب المستهدفين في GET أيضاً
        if not request.user.is_superuser:
            teacher = request.user.teacher_profile
            form.fields['specific_students'].queryset = Student.objects.filter(
                enrollment__course=course,
                enrollment__teacher=teacher,
                enrollment__is_completed=False
            ).distinct()
        else:
            form.fields['specific_students'].queryset = Student.objects.filter(
                enrollment__course=course,
                enrollment__is_completed=False
            ).distinct()

    return render(request, 'quiz/create_quiz.html', {'form': form, 'course': course})


@login_required
@user_passes_test(is_teacher_or_superuser)
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # حماية إضافية للمعلم
    if not request.user.is_superuser:
        teacher = request.user.teacher_profile
        # التحقق من أن مادة الكورس التابع له الاختبار تقع ضمن تخصصات المعلم الحالي
        if quiz.course.subject not in teacher.subjects.all():
            messages.error(request, "ليس لديك الصلاحية للتعديل على اختبارات هذا الكورس.")
            return redirect('quiz:quiz_dashboard')
            
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        
        question_type = request.POST.get('question_type', 'mcq')
        is_essay = (question_type == 'essay')
        
        is_valid = form.is_valid() if is_essay else (form.is_valid() and formset.is_valid())
        
        if is_valid:
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            if not is_essay:
                # Save the related choices
                choices = formset.save(commit=False)
                for choice in choices:
                    choice.question = question
                    choice.save()
                
                for obj in formset.deleted_objects:
                    obj.delete()
            
            messages.success(request, "تم إضافة السؤال بنجاح.")
            
            if 'save_and_add_another' in request.POST:
                return redirect('quiz:add_question', quiz_id=quiz.id)
            else:
                return redirect('quiz:quiz_dashboard') 
        else:
            if not is_essay and formset.non_form_errors():
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
        
        has_essay = any(q.question_type == 'essay' for q in questions)
        total_marks = sum(q.marks for q in questions)
        earned_marks = 0.0
        
        if student:
            # إنشاء محاولة وحفظها
            attempt = QuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                score=0.0,
                passed=False,
                status='pending' if has_essay else 'graded'
            )
            
            # حفظ الإجابات التفصيلية
            from .models import StudentAnswer
            for question in questions:
                if question.question_type == 'essay':
                    essay_ans = request.POST.get(f'question_{question.id}', '').strip()
                    StudentAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        essay_answer=essay_ans,
                        marks_earned=0.0,
                        is_graded=False
                    )
                else:
                    selected_choice_id = request.POST.get(f'question_{question.id}')
                    selected_choice = None
                    marks_earned = 0.0
                    if selected_choice_id:
                        try:
                            selected_choice = Choice.objects.get(id=int(selected_choice_id), question=question)
                            if selected_choice.is_correct:
                                marks_earned = float(question.marks)
                                earned_marks += marks_earned
                        except (ValueError, Choice.DoesNotExist):
                            pass
                    StudentAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=selected_choice,
                        marks_earned=marks_earned,
                        is_graded=True
                    )
            
            # إذا لم يحتوي على أسئلة مقالية، يتم احتساب النتيجة والنجاح فوراً
            if not has_essay:
                percentage = (earned_marks / total_marks) * 100 if total_marks > 0 else 0
                attempt.score = percentage
                attempt.passed = percentage >= quiz.pass_score
                attempt.save()
                messages.success(request, f"تم تسليم إجاباتك بنجاح! درجتك المباشرة: {percentage:.1f}%")
            else:
                messages.success(request, "تم تسليم إجاباتك بنجاح! يحتوي الاختبار على أسئلة مقالية وسيتم تصحيحها ومراجعتها من قبل المعلم قريباً.")
        else:
            # حساب مسؤول (لمحاكاة الحل)
            for question in questions:
                if question.question_type != 'essay':
                    selected_choice_id = request.POST.get(f'question_{question.id}')
                    if selected_choice_id:
                        try:
                            selected_choice = Choice.objects.get(id=int(selected_choice_id), question=question)
                            if selected_choice.is_correct:
                                earned_marks += question.marks
                        except (ValueError, Choice.DoesNotExist):
                            pass
            percentage = (earned_marks / total_marks) * 100 if total_marks > 0 else 0
            if has_essay:
                messages.info(request, f"حساب مسؤول: تم محاكاة التسليم. النسبة المحققة للأسئلة التلقائية: {percentage:.1f}% (يحتوي الاختبار على جزء مقالي)")
            else:
                messages.info(request, f"حساب مسؤول: تم تقييم إجاباتك بنجاح! النتيجة: {percentage:.1f}%")
            
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


@login_required
def review_quiz(request, attempt_id):
    """عرض ومراجعة إجابات الطالب في محاولة معينة."""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # حماية IDOR: الطالب يجب أن يرى محاولته فقط، المعلم يجب أن يرى محاولات طلابه فقط
    if not request.user.is_superuser:
        if hasattr(request.user, 'student_profile'):
            if attempt.student != request.user.student_profile:
                messages.error(request, "غير مصرح لك بمشاهدة هذه المحاولة.")
                return redirect('profile_view')
        elif hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
            # التحقق من أن الطالب مسجل لدى المعلم في هذا الكورس
            is_enrolled = Enrollment.objects.filter(
                student=attempt.student, 
                course=attempt.quiz.course, 
                teacher=teacher
            ).exists()
            if not is_enrolled:
                messages.error(request, "غير مصرح لك بمشاهدة هذه المحاولة لأن الطالب ليس في مجموعتك الدراسية.")
                return redirect('profile_view')
        else:
            messages.error(request, "غير مصرح لك بالدخول لهذه الصفحة.")
            return redirect('profile_view')
            
    answers = attempt.answers.all().select_related('question').prefetch_related('question__choices')
    
    return render(request, 'quiz/review_quiz.html', {
        'attempt': attempt,
        'answers': answers,
    })


@login_required
@user_passes_test(is_teacher_or_superuser)
def grade_quiz(request, attempt_id):
    """واجهة للمعلم لتصحيح الأسئلة المقالية وإسناد الدرجات للطلاب."""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # حماية IDOR: المعلم يجب أن يدرس الطالب في هذا الكورس
    if not request.user.is_superuser:
        teacher = request.user.teacher_profile
        is_enrolled = Enrollment.objects.filter(
            student=attempt.student, 
            course=attempt.quiz.course, 
            teacher=teacher
        ).exists()
        if not is_enrolled:
            messages.error(request, "غير مصرح لك بتصحيح هذا الاختبار لأن الطالب ليس من طلابك.")
            return redirect('profile_view')
            
    # جلب الإجابات التي تحتاج لتصحيح أو المقالية
    essay_answers = attempt.answers.filter(question__question_type='essay').select_related('question')
    
    if request.method == 'POST':
        for ans in essay_answers:
            marks_input = request.POST.get(f'marks_answer_{ans.id}')
            if marks_input is not None:
                try:
                    marks_earned = float(marks_input)
                    if marks_earned < 0:
                        marks_earned = 0.0
                    elif marks_earned > ans.question.marks:
                        marks_earned = float(ans.question.marks)
                        
                    ans.marks_earned = marks_earned
                    ans.is_graded = True
                    ans.save()
                except ValueError:
                    pass
                    
        # بعد تصحيح كافة الأسئلة المقالية، نحتسب النتيجة الإجمالية للمحاولة
        all_answers = attempt.answers.all()
        all_graded = all(ans.is_graded for ans in all_answers)
        
        if all_graded:
            total_marks = sum(ans.question.marks for ans in all_answers)
            total_earned = sum(ans.marks_earned for ans in all_answers)
            percentage = (total_earned / total_marks) * 100 if total_marks > 0 else 0
            
            attempt.score = percentage
            attempt.passed = percentage >= attempt.quiz.pass_score
            attempt.status = 'graded'
            attempt.save()
            
            messages.success(request, f"تم تصحيح اختبار الطالب {attempt.student.name} بنجاح! النتيجة النهائية: {percentage:.1f}%")
        else:
            messages.warning(request, "تم حفظ الدرجات جزئياً، يرجى استكمال تصحيح باقي الأسئلة.")
            
        return redirect('profile_view')
        
    return render(request, 'quiz/grade_quiz.html', {
        'attempt': attempt,
        'essay_answers': essay_answers
    })