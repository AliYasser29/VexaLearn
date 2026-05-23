import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5)
def send_email_task(self, subject, message, recipient_list):
    """
    Celery task to send an email with exponential backoff retry mechanism.
    """
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"Successfully sent email to {recipient_list}")
    except Exception as exc:
        logger.warning(f"Failed to send email to {recipient_list}. Retrying...")
        # Exponential backoff: 60s, 120s, 240s, 480s, 960s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def notify_supervisor_new_student_task(student_id):
    from core.models import Student
    try:
        student = Student.objects.get(id=student_id)
        if student.supervisor and student.supervisor.email:
            site_url = "https://vexalearn.cloud"
            
            subject = f'تنبيه: تم إسناد طالب جديد إليك - {student.name}'
            message = f"""
            مرحباً {student.supervisor.name}،
            
            تم تسجيل طالب جديد وإسناده لإشرافك.
            
            بيانات الطالب:
            --------------------------
            الاسم: {student.name}
            السنة الدراسية: {student.academic_year}
            --------------------------
            
            يرجى متابعة الطالب من خلال لوحة التحكم.
            رابط المنصة: {site_url}/dashboard
            """
            send_email_task.delay(subject, message, [student.supervisor.email])
    except Student.DoesNotExist:
        pass

@shared_task
def notify_teachers_new_student_task(student_id, new_teacher_ids):
    from core.models import Student, Teacher
    try:
        student = Student.objects.get(id=student_id)
        new_teachers = Teacher.objects.filter(id__in=new_teacher_ids)
        site_url = "https://vexalearn.cloud"
        
        for teacher in new_teachers:
            if teacher.email:
                subject = f'طالب جديد في مجموعتك - {student.name}'
                message = f"""
                مرحباً أستاذ/ة {teacher.name}،
                
                تم إضافة الطالب ({student.name}) إلى قائمة طلابك.
                
                بيانات الطالب:
                --------------------------
                الاسم: {student.name}
                السنة الدراسية: {student.academic_year}
                --------------------------
                
                يرجى التواصل معه ومتابعة تقدمه.
                {site_url}/chat
                """
                send_email_task.delay(subject, message, [teacher.email])
    except Student.DoesNotExist:
        pass

@shared_task
def notify_attendance_change_task(attendance_id):
    from core.models import Attendance
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        enrollment = attendance.enrollment
        student = enrollment.student
        course = enrollment.course
        parent_email = student.parent_email

        if parent_email:
            current_session_number = enrollment.attendances.count()
            total_sessions = course.sessions_count
            remaining_sessions = total_sessions - current_session_number
            if remaining_sessions < 0: remaining_sessions = 0

            renewal_notice = ""
            if total_sessions > 0:
                threshold = total_sessions * 0.25
                if remaining_sessions <= threshold and remaining_sessions > 0:
                    renewal_notice = """
                    🔴 تنبيه هام:
                    لقد شارف الاشتراك على الانتهاء. يرجى مراجعة الإدارة لتجديد الاشتراك.
                    """
                elif remaining_sessions == 0:
                    renewal_notice = """
                    🔴 تنبيه هام:
                    لقد انتهت جميع حصص هذا الكورس. يرجى التجديد فوراً.
                    """

            status_text = "حضور ✅" if attendance.status == 'present' else "غياب ❌"

            subject = f'تنبيه حصة: {student.name} - كورس {course.name}'
            message = f"""
            مرحباً ولي أمر الطالب/ة {student.name}،
            
            نود إعلامكم بأنه تم تسجيل "{status_text}" للطالب اليوم في كورس {course.name}.
            
            تفاصيل الحصة:
            --------------------------------------------------
            الحالة: {status_text}
            رقم الحصة: {current_session_number} من أصل {total_sessions}
            المتبقي في الكورس: {remaining_sessions} حصص
            --------------------------------------------------
            {renewal_notice}
            
            تاريخ التسجيل: {attendance.date}
            
            إدارة الأكاديمية
            """
            send_email_task.delay(subject, message, [parent_email])
    except Attendance.DoesNotExist:
        pass
