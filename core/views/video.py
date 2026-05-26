import time
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from core.models import Enrollment
from agora_token_builder import RtcTokenBuilder

@login_required
def video_call_view(request, room_name):
    """إنشاء وإدارة جلسة الفيديو باستخدام Agora."""
    APP_ID = settings.AGORA_APP_ID
    APP_CERTIFICATE = settings.AGORA_APP_CERTIFICATE

    if not APP_ID or not APP_CERTIFICATE:
        messages.error(request, "إعدادات الفيديو غير مكتملة في السيرفر.")
        return redirect('chat_home')

    # Authorization Check
    import re
    is_authorized = False
    
    # 1. Match VexaLearn_<user1_id>_<user2_id> format
    match = re.match(r'^VexaLearn_(\d+)_(\d+)$', room_name)
    if match:
        try:
            u1_id = int(match.group(1))
            u2_id = int(match.group(2))
            
            current_user = request.user
            if current_user.id in [u1_id, u2_id]:
                other_user_id = u2_id if current_user.id == u1_id else u1_id
                
                try:
                    other_user = User.objects.get(id=other_user_id, is_active=True)
                    
                    # A. Superuser or Manager on either side has global relationship
                    if (current_user.is_superuser or hasattr(current_user, 'manager_profile') or 
                            other_user.is_superuser or hasattr(other_user, 'manager_profile')):
                        is_authorized = True
                    else:
                        # B. Check student-teacher, student-supervisor, or teacher-supervisor relations
                        def check_student_teacher(u_student, u_teacher):
                            if hasattr(u_student, 'student_profile') and hasattr(u_teacher, 'teacher_profile'):
                                student = u_student.student_profile
                                teacher = u_teacher.teacher_profile
                                if Enrollment.objects.filter(student=student, teacher=teacher, is_completed=False).exists():
                                    return True
                                if student.teachers.filter(id=teacher.id).exists():
                                    return True
                            return False

                        def check_student_supervisor(u_student, u_supervisor):
                            if hasattr(u_student, 'student_profile') and hasattr(u_supervisor, 'supervisor_profile'):
                                student = u_student.student_profile
                                supervisor = u_supervisor.supervisor_profile
                                if student.supervisor == supervisor:
                                    return True
                            return False

                        def check_teacher_supervisor(u_teacher, u_supervisor):
                            if hasattr(u_teacher, 'teacher_profile') and hasattr(u_supervisor, 'supervisor_profile'):
                                teacher = u_teacher.teacher_profile
                                supervisor = u_supervisor.supervisor_profile
                                if Enrollment.objects.filter(teacher=teacher, student__supervisor=supervisor, is_completed=False).exists():
                                    return True
                            return False

                        if check_student_teacher(current_user, other_user) or check_student_teacher(other_user, current_user):
                            is_authorized = True
                        elif check_student_supervisor(current_user, other_user) or check_student_supervisor(other_user, current_user):
                            is_authorized = True
                        elif check_teacher_supervisor(current_user, other_user) or check_teacher_supervisor(other_user, current_user):
                            is_authorized = True
                        
                        # C. Fallback to general chat permission logic (Q objects)
                        if not is_authorized:
                            q_objects = Q()
                            if hasattr(current_user, 'supervisor_profile'):
                                supervisor_profile = current_user.supervisor_profile
                                q_objects = Q(student_profile__supervisor=supervisor_profile) | \
                                            Q(teacher_profile__student__supervisor=supervisor_profile)
                            elif hasattr(current_user, 'teacher_profile'):
                                teacher_profile = current_user.teacher_profile
                                q_objects = Q(student_profile__enrollment__teacher=teacher_profile) | \
                                            Q(supervisor_profile__students__enrollment__teacher=teacher_profile)
                            elif hasattr(current_user, 'student_profile'):
                                student_profile = current_user.student_profile
                                q_objects = Q(teacher_profile__enrollment__student=student_profile) | \
                                            Q(supervisor_profile__students=student_profile)
                            
                            if q_objects and User.objects.filter(q_objects).filter(id=other_user_id).exists():
                                is_authorized = True
                except User.DoesNotExist:
                    is_authorized = False
        except ValueError:
            is_authorized = False

    # 2. Match 'general' format
    elif room_name == 'general':
        if (request.user.is_superuser or 
                hasattr(request.user, 'manager_profile') or 
                hasattr(request.user, 'supervisor_profile') or 
                hasattr(request.user, 'teacher_profile')):
            is_authorized = True
        elif hasattr(request.user, 'student_profile'):
            if Enrollment.objects.filter(student=request.user.student_profile, is_completed=False).exists():
                is_authorized = True

    # 3. Match numeric course_id
    else:
        try:
            course_id_int = int(room_name)
            if request.user.is_superuser or hasattr(request.user, 'manager_profile'):
                is_authorized = True
            elif hasattr(request.user, 'teacher_profile'):
                if Enrollment.objects.filter(course_id=course_id_int, teacher=request.user.teacher_profile).exists():
                    is_authorized = True
            elif hasattr(request.user, 'student_profile'):
                if Enrollment.objects.filter(course_id=course_id_int, student=request.user.student_profile, is_completed=False).exists():
                    is_authorized = True
        except ValueError:
            is_authorized = False

    if not is_authorized:
        messages.error(request, "غير مصرح لك بدخول هذه الجلسة.")
        return redirect('chat_home')

    uid = request.user.id 
    expiration_time_in_seconds = 7200 
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds
    role = 1 

    try:
        token = RtcTokenBuilder.buildTokenWithUid(
            APP_ID, 
            APP_CERTIFICATE, 
            room_name, 
            uid, 
            role, 
            privilege_expired_ts
        )
    except Exception as e:
        print(f"Error generating token: {e}")
        messages.error(request, "حدث خطأ أثناء إنشاء جلسة الفيديو.")
        return redirect('chat_home')

    context = {
        'room_name': room_name,
        'app_id': APP_ID,
        'token': token,
        'uid': uid,
        'user_name': request.user.first_name or request.user.username,
    }
    return render(request, 'core/video_call.html', context)
