from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 1. المصادقة العامة (المشرفين)
    path('login/', views.unified_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 2. لوحة تحكم المشرف وإدارة الحصص
    path('dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('mark-attendance/<int:enrollment_id>/', views.mark_attendance, name='mark_attendance'),
    path('mark-absence/<int:enrollment_id>/', views.mark_absence, name='mark_absence'),
    path('complete-course/<int:enrollment_id>/', views.complete_course, name='complete_course'),

    # 3. لوحة الإدارة (إضافة الطلاب والاشتراكات)
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/<int:student_id>/', views.admin_panel, name='admin_panel_edit'),
    path('add-enrollment/<int:student_id>/', views.add_enrollment, name='add_enrollment'),

    # 4. نظام الشات
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

    path('super-monitor/', views.universal_chat_monitor, name='universal_chat_monitor'),


    path('profile/', views.profile_view, name='profile_view'),
    path('switch-role/<str:role_name>/', views.switch_role, name='switch_role'),


    path('check-messages/', views.check_new_messages, name='check_new_messages'),

    path('ajax/load-teachers/', views.load_teachers, name='ajax_load_teachers'),

    path('materials/upload/', views.upload_material, name='upload_material'),
    path('course/<int:course_id>/materials/', views.course_materials, name='course_materials'),

    path('ajax/load-education-types/', views.load_education_types, name='ajax_load_education_types'),
    path('ajax/load-academic-years/', views.load_academic_years, name='ajax_load_academic_years'),
    path('students/directory/', views.student_directory, name='student_directory'),
]