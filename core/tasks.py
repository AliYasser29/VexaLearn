import logging
import threading
import re
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import escape

logger = logging.getLogger(__name__)

def convert_plain_text_to_html(subject, message):
    """
    Converts plain text Arabic/English messages to highly readable RTL HTML.
    Prevents text scrambled/reversed issues with mixed Arabic and English/Numbers.
    """
    lines = [line.strip() for line in message.split('\n')]
    
    greeting = ""
    paragraphs = []
    details = []
    footer_lines = []
    actions = []
    
    # Simple regex for finding URLs
    url_pattern = re.compile(r'(https?://\S+)')
    
    in_details = False
    
    for line in lines:
        if not line:
            continue
        
        # Check if greeting line
        if any(greet in line for greet in ["مرحباً", "مرحبا", "السيد", "السيدة", "أستاذ", "أستاذ/ة"]):
            greeting = line
            continue
        
        # Check if footer/signoff line
        if any(sign in line for sign in ["إدارة", "مع خالص التقدير", "تحيات", "كادر"]):
            footer_lines.append(line)
            continue
            
        # Check if detail boundary line
        if line.startswith('---') or line.startswith('___') or line.startswith('***'):
            in_details = not in_details
            continue
            
        # Key-Value detection
        if ':' in line or '：' in line:
            parts = line.split(':', 1) if ':' in line else line.split('：', 1)
            key = parts[0].strip()
            val = parts[1].strip()
            
            # Check if value is a URL
            urls = url_pattern.findall(val)
            if urls:
                actions.append((key, urls[0]))
            else:
                details.append((key, val))
        else:
            # Check if there is a URL in the line
            urls = url_pattern.findall(line)
            if urls:
                clean_line = url_pattern.sub('', line).strip()
                label = clean_line if clean_line else "انتقل إلى الرابط"
                actions.append((label, urls[0]))
            else:
                if in_details:
                    details.append(("", line))
                else:
                    paragraphs.append(line)

    # Escape HTML to prevent injection and format safely
    greeting_html = ""
    if greeting:
        greeting_html = f'<p style="font-size: 16px; font-weight: 600; color: #1e1b4b; margin-top: 0; margin-bottom: 20px; text-align: right; direction: rtl;">{escape(greeting)}</p>'
        
    paragraphs_html = ""
    for para in paragraphs:
        paragraphs_html += f'<p style="font-size: 15px; color: #4b5563; line-height: 1.6; margin-top: 0; margin-bottom: 16px; text-align: right; direction: rtl;">{escape(para)}</p>'
        
    details_html = ""
    if details:
        details_rows = ""
        for key, val in details:
            escaped_key = escape(key)
            escaped_val = escape(val)
            
            if not escaped_key:
                details_rows += f"""
                <tr>
                    <td colspan="2" style="padding: 10px 0; font-size: 14px; color: #4b5563; text-align: right; line-height: 1.5; direction: rtl;">{escaped_val}</td>
                </tr>
                """
            else:
                # Format credentials with monospace box
                is_credential = any(word in key for word in ["اسم المستخدم", "كلمة المرور", "username", "password"])
                is_status = "الحالة" in key
                
                if is_credential:
                    val_html = f'<code style="background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 4px 8px; border-radius: 6px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 14px; color: #4f46e5; letter-spacing: 0.5px; direction: ltr; display: inline-block;">{escaped_val}</code>'
                elif is_status:
                    badge_color = "#10b981" if "حضور" in val or "✅" in val else "#ef4444"
                    bg_color = "#ecfdf5" if "حضور" in val or "✅" in val else "#fef2f2"
                    val_html = f'<span style="background-color: {bg_color}; color: {badge_color}; padding: 4px 10px; border-radius: 9999px; font-size: 13px; font-weight: 700; display: inline-block; border: 1px solid {badge_color}33; direction: rtl;">{escaped_val}</span>'
                else:
                    # Direction LTR for codes, numbers, phones to keep order intact
                    if re.match(r'^[a-zA-Z0-9\s\-\+\.\_\@\/]+$', val):
                        val_html = f'<span style="direction: ltr; display: inline-block;">{escaped_val}</span>'
                    else:
                        val_html = escaped_val
                
                details_rows += f"""
                <tr>
                    <td style="padding: 12px 0 12px 10px; font-size: 14px; font-weight: 600; color: #64748b; width: 140px; text-align: right; border-bottom: 1px solid #f1f5f9; direction: rtl;" valign="top">{escaped_key}</td>
                    <td style="padding: 12px 0; border-bottom: 1px solid #f1f5f9; text-align: right; font-size: 14px; color: #1f2937;" valign="middle">{val_html}</td>
                </tr>
                """
        
        details_html = f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 8px 20px; margin: 24px 0; direction: rtl; text-align: right;">
            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-collapse: collapse;">
                {details_rows}
            </table>
        </div>
        """
        
    action_html = ""
    if actions:
        buttons = ""
        for label, url in actions:
            clean_label = label.replace("رابط المنصة", "").replace("رابط منصة التواصل", "").replace("رابط", "").strip()
            if not clean_label or clean_label == ":":
                clean_label = "اضغط هنا للدخول"
            
            buttons += f"""
            <table border="0" cellspacing="0" cellpadding="0" style="display: inline-block; margin: 5px 10px;">
                <tr>
                    <td align="center" style="border-radius: 8px; background-color: #4f46e5;">
                        <a href="{escape(url)}" target="_blank" style="display: inline-block; background-color: #4f46e5; border: 1px solid #4f46e5; border-radius: 8px; color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: bold; padding: 12px 24px; text-decoration: none; text-align: center;">
                            {escape(clean_label)}
                        </a>
                    </td>
                </tr>
            </table>
            """
        action_html = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 24px; margin-bottom: 12px;">
            <tr>
                <td align="center">
                    {buttons}
                </td>
            </tr>
        </table>
        """
        
    footer_html = ""
    if footer_lines:
        for fline in footer_lines:
            footer_html += f'<p style="margin: 0; font-size: 13px; font-weight: 600; color: #4b5563; line-height: 1.6; text-align: center; direction: rtl;">{escape(fline)}</p>'
    else:
        footer_html = '<p style="margin: 0; font-size: 13px; font-weight: 600; color: #4b5563; line-height: 1.6; text-align: center; direction: rtl;">إدارة أكاديمية VexaLearn</p>'

    # Base HTML template with absolute RTL support
    html_template = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(subject)}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 100% !important;
            background-color: #f4f4f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            -webkit-font-smoothing: antialiased;
            text-size-adjust: none;
        }}
        table {{
            border-collapse: collapse;
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f5; direction: rtl; text-align: right;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f4f5; padding: 24px 12px;">
        <tr>
            <td align="center">
                <table width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.025); border: 1px solid #e4e4e7; border-collapse: collapse;">
                    <tr>
                        <td height="6" style="background: linear-gradient(to left, #4f46e5, #06b6d4);"></td>
                    </tr>
                    <tr>
                        <td style="padding: 24px 32px 16px 32px; text-align: center; border-bottom: 1px solid #f4f4f5;">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #1e1b4b; font-family: 'Segoe UI', Arial, sans-serif;">VexaLearn</h1>
                            <p style="margin: 4px 0 0 0; font-size: 12px; color: #71717a; font-weight: 500;">منصة التعلم الذكي</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 32px 32px 24px 32px; direction: rtl; text-align: right;">
                            <h2 style="margin-top: 0; margin-bottom: 20px; font-size: 18px; font-weight: 700; color: #1f2937; line-height: 1.4; direction: rtl; text-align: right;">{escape(subject)}</h2>
                            {greeting_html}
                            {paragraphs_html}
                            {details_html}
                            {action_html}
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #fafafa; padding: 24px 32px; text-align: center; border-top: 1px solid #f4f4f5;">
                            {footer_html}
                            <p style="margin: 12px 0 0 0; font-size: 11px; color: #a1a1aa; text-align: center;">
                                لقد أُرسلت هذه الرسالة تلقائياً من منصة VexaLearn.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return html_template

@shared_task(bind=True, max_retries=5)
def send_email_task(self, subject, message, recipient_list, html_message=None):
    """
    Celery task to send an email.
    Automatically converts plain text messages to premium RTL HTML formats if html_message is None.
    """
    try:
        if html_message is None and message:
            html_message = convert_plain_text_to_html(subject, message)
            
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"Successfully sent email to {recipient_list}")
    except Exception as exc:
        logger.error(f"Failed to send email to {recipient_list}: {exc}")
        raise self.retry(exc=exc, countdown=60)

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
