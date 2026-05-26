from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('dashboard/', views.quiz_dashboard, name='quiz_dashboard'),
    path('create/<int:course_id>/', views.create_quiz, name='create_quiz'),
    path('add-question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('review/<int:attempt_id>/', views.review_quiz, name='review_quiz'),
    path('grade/<int:attempt_id>/', views.grade_quiz, name='grade_quiz'),
]