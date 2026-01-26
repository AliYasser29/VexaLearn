from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Course, Enrollment
from .models import Quiz, Question, Choice, QuizAttempt
from .forms import QuizForm, QuestionForm

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
        
        # استقبال الاختيارات يدوياً من الـ HTML
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        correct_option = request.POST.get('correct_option') 

        if form.is_valid() and option1 and option2: # يجب وجود خيارين على الأقل
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            # حفظ الاختيارات
            options = [option1, option2, option3, option4]
            for idx, opt_text in enumerate(options, 1):
                if opt_text: # إذا كان الحقل ممتلئاً
                    is_correct = (str(idx) == correct_option)
                    Choice.objects.create(question=question, text=opt_text, is_correct=is_correct)
            
            messages.success(request, "تم إضافة السؤال بنجاح.")
            
            if 'save_and_add_another' in request.POST:
                return redirect('add_question', quiz_id=quiz.id)
            else:
                return redirect('/') 
    else:
        form = QuestionForm()

    return render(request, 'quiz/add_question.html', {'form': form, 'quiz': quiz})


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
            return redirect('profile_view')

        if quiz.specific_students.exists():
            if student not in quiz.specific_students.all():
                messages.error(request, "هذا الاختبار غير مخصص لك.")
                return redirect('profile_view')
        # ----------------------------------------------------

        if QuizAttempt.objects.filter(student=student, quiz=quiz).exists():
            messages.warning(request, "لقد قمت بأداء هذا الاختبار مسبقاً.")
            return redirect('profile_view')