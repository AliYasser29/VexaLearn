from django.db import models
from core.models import Course, Student
from simple_history.models import HistoricalRecords

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes', verbose_name="الكورس")
    
    specific_students = models.ManyToManyField(
        Student, 
        blank=True, 
        related_name='private_quizzes',
        verbose_name="تخصيص لطلاب محددين (اختياري)"
    )
    # ---------------------

    title = models.CharField(max_length=200, verbose_name="عنوان الاختبار")
    description = models.TextField(blank=True, verbose_name="وصف الاختبار")
    duration = models.PositiveIntegerField(help_text="المدة بالدقائق", verbose_name="مدة الاختبار")
    pass_score = models.PositiveIntegerField(default=50, help_text="النسبة المئوية للنجاح (مثلاً 50)", verbose_name="درجة النجاح")
    session_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="رقم الحصة")
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        type_label = "خاص" if self.specific_students.exists() else "عام"
        session_text = f" - الحصة {self.session_number}" if self.session_number else " - كامل الكورس"
        return f"{self.title} ({self.course.name}{session_text} - {type_label})"
        
    class Meta:
        verbose_name = "اختبار"
        verbose_name_plural = "الاختبارات"


class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'اختيار من متعدد'),
        ('tf', 'صح أو خطأ'),
        ('essay', 'سؤال مقالي'),
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="نص السؤال")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mcq', verbose_name="نوع السؤال")
    marks = models.PositiveIntegerField(default=1, verbose_name="الدرجة")
    history = HistoricalRecords()

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255, verbose_name="نص الاختيار")
    is_correct = models.BooleanField(default=False, verbose_name="إجابة صحيحة؟")
    history = HistoricalRecords()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "اختيار"
        verbose_name_plural = "الاختيارات"


class QuizAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(verbose_name="الدرجة المحققة")
    passed = models.BooleanField(default=False, verbose_name="ناجح؟")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاختبار")
    status = models.CharField(
        max_length=20,
        choices=(('pending', 'قيد المراجعة'), ('graded', 'تم التصحيح')),
        default='graded',
        verbose_name="حالة التصحيح"
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "نتيجة اختبار"
        verbose_name_plural = "نتائج الاختبارات"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers', verbose_name="محاولة الاختبار")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="السؤال")
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الخيار المختار")
    essay_answer = models.TextField(null=True, blank=True, verbose_name="الإجابة المقالية")
    marks_earned = models.FloatField(default=0.0, verbose_name="الدرجة المستحقة")
    is_graded = models.BooleanField(default=False, verbose_name="تم تصحيحه؟")
    history = HistoricalRecords()

    def __str__(self):
        return f"إجابة {self.attempt.student.name} - السؤال: {self.question.text[:30]}"

    class Meta:
        verbose_name = "إجابة الطالب"
        verbose_name_plural = "إجابات الطلاب"