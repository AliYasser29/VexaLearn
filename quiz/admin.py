from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4  # عدد الخانات الفارغة للاختيارات

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]  # لإضافة الاختيارات داخل صفحة السؤال مباشرة
    list_display = ('text', 'quiz', 'question_type', 'marks')
    list_filter = ('quiz',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True # يسمح بالدخول لتعديل السؤال وإضافة اختياراته

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'course', 'duration', 'pass_score')
    list_filter = ('course',)

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'passed', 'completed_at')
    list_filter = ('quiz', 'passed')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)