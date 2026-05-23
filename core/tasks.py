import logging
import threading
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def _send_email_thread(subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"Successfully sent email in background to {recipient_list}")
    except Exception as exc:
        logger.error(f"Failed to send background email to {recipient_list}: {exc}")

@shared_task(bind=True, max_retries=5)
def send_email_task(self, subject, message, recipient_list):
    """
    Celery task to send an email. Since we run in eager mode without Redis,
    we spawn a background thread so the main request thread doesn't wait (non-blocking).
    """
    # Spawn background thread to send the email concurrently
    thread = threading.Thread(
        target=_send_email_thread,
        args=(subject, message, recipient_list)
    )
    thread.daemon = True
    thread.start()
    logger.info(f"Spawned background thread to send email to {recipient_list}")

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

            progress_notice = ""
            if total_sessions > 0:
                if current_session_number == total_sessions // 2:
                    progress_notice = """
                    🎉 تهانينا! لقد أكمل الطالب نصف حصص الكورس (50%). نأمل أن تكونوا راضين عن تقدمه!
                    """
                elif current_session_number == int(total_sessions * 0.75):
                    progress_notice = """
                    🎉 تهانينا! لقد أكمل الطالب 75% من حصص الكورس. مستوى رائع ومتابعة ممتازة!
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
            {progress_notice}
            {renewal_notice}
            
            تاريخ التسجيل: {attendance.date}
            
            إدارة الأكاديمية
            """
            send_email_task.delay(subject, message, [parent_email])
    except Attendance.DoesNotExist:
        pass


@shared_task
def notify_parent_new_course_task(enrollment_id):
    from core.models import Enrollment
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        student = enrollment.student
        course = enrollment.course
        parent_email = student.parent_email
        
        if parent_email:
            subject = f'📚 تسجيل كورس جديد للطالب/ة: {student.name}'
            message = f"""
            مرحباً ولي أمر الطالب/ة {student.name}،
            
            يسعدنا إعلامكم بأنه تم تسجيل الطالب بنجاح في كورس جديد.
            
            تفاصيل الكورس:
            --------------------------------------------------
            اسم الكورس: {course.name}
            المعلم: {enrollment.teacher.name if enrollment.teacher else 'سيتم تحديده لاحقاً'}
            عدد الحصص الإجمالي: {course.sessions_count} حصة
            تاريخ بدء الاشتراك: {enrollment.start_date}
            --------------------------------------------------
            
            نتمنى للطالب رحلة تعليمية مميزة ومليئة بالنجاح.
            
            إدارة الأكاديمية
            """
            send_email_task.delay(subject, message, [parent_email])
    except Enrollment.DoesNotExist:
        pass


@shared_task
def notify_teacher_new_enrollment_task(enrollment_id):
    from core.models import Enrollment
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        student = enrollment.student
        course = enrollment.course
        teacher = enrollment.teacher
        
        if teacher and teacher.email:
            site_url = "https://vexalearn.cloud"
            subject = f'👨‍🏫 إسناد طالب جديد إليك - كورس {course.name}'
            message = f"""
            مرحباً أستاذ/ة {teacher.name}،
            
            تم إسناد طالب جديد إليك في كورس {course.name}.
            
            تفاصيل الطالب والكورس:
            --------------------------------------------------
            الاسم: {student.name}
            السنة الدراسية: {student.academic_year.name if student.academic_year else 'غير محدد'}
            الكورس: {course.name}
            تاريخ بدء الاشتراك: {enrollment.start_date}
            --------------------------------------------------
            
            يرجى التواصل مع الطالب ومتابعة تقدمه عبر منصة الشات.
            🔗 رابط منصة التواصل: {site_url}/chat
            
            مع خالص التقدير،
            إدارة الشؤون الأكاديمية
            """
            send_email_task.delay(subject, message, [teacher.email])
    except Enrollment.DoesNotExist:
        pass
