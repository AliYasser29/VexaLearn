from .auth import unified_login_view, switch_role, profile_view, get_dashboard_url_for_user
from .dashboards import supervisor_dashboard, student_dashboard, instructor_dashboard, student_directory
from .attendance import mark_attendance, mark_absence, complete_course
from .admin import admin_panel, add_enrollment
from .chat import chat_room, check_new_messages, submit_daily_report, monitor_student_chat, student_full_chat_log, universal_chat_monitor
from .materials import upload_material, course_materials
from .video import video_call_view
from .ajax import load_teachers, load_education_types, load_academic_years
from .public import landing_page, academy_details, games_page
