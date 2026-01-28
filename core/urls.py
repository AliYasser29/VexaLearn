from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import management_login

urlpatterns = [
    # 1. المصادقة العامة (المشرفين)
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 2. لوحة تحكم المشرف وإدارة الحصص
    path('dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('mark-attendance/<int:enrollment_id>/', views.mark_attendance, name='mark_attendance'),
    path('mark-absence/<int:enrollment_id>/', views.mark_absence, name='mark_absence'),
    path('complete-course/<int:enrollment_id>/', views.complete_course, name='complete_course'),

    # 3. لوحة الإدارة (إضافة الطلاب والاشتراكات)
    path('management/login/', management_login, name='management_login'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('add-enrollment/<int:student_id>/', views.add_enrollment, name='add_enrollment'),

    # 4. نظام الشات
    # رابط دخول الشات
    path('chat/login/', auth_views.LoginView.as_view(
        template_name='core/chat_login.html',
        redirect_authenticated_user=True,
        next_page='chat_home'
    ), name='chat_login'),

    # --- (الجديد) رابط خروج الشات ---
    path('chat/logout/', auth_views.LogoutView.as_view(next_page='chat_login'), name='chat_logout'),
    # -------------------------------

    path('chat/', views.chat_room, name='chat_home'),           # الصفحة الرئيسية للشات
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'), # محادثة خاصة

    # مراقبة الشات (للمشرفين)
    path('monitor-chat/<int:student_id>/', views.monitor_student_chat, name='monitor_student_chat'),

    
    path('submit-report/<int:student_id>/', views.submit_daily_report, name='submit_daily_report'),
    

    path('dashboard/student/<int:student_id>/chat-log/', views.student_full_chat_log, name='student_full_chat_log'),
    path('video-call/<str:room_name>/', views.video_call_view, name='video_call'),

    path('', views.landing_page, name='landing_page'), # الصفحة الرئيسية
    path('academy/<int:academy_id>/', views.academy_details, name='academy_details'),
    path('games/', views.games_page, name='games_page'),

    path('super-monitor/login/', views.superuser_custom_login, name='superuser_custom_login'),
    path('super-monitor/', views.universal_chat_monitor, name='universal_chat_monitor'),


    path('profile/', views.profile_view, name='profile_view'),

    path('publiclogin/', views.public_login, name='plogin'), 


    path('check-messages/', views.check_new_messages, name='check_new_messages'),

    path('ajax/load-teachers/', views.load_teachers, name='ajax_load_teachers'),

    path('materials/upload/', views.upload_material, name='upload_material'),
    path('course/<int:course_id>/materials/', views.course_materials, name='course_materials'),

    path('ajax/load-education-types/', views.load_education_types, name='ajax_load_education_types'),
    path('ajax/load-academic-years/', views.load_academic_years, name='ajax_load_academic_years'),
]