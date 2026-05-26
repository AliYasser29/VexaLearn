from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.models import Enrollment, Attendance, Notification

@login_required
def mark_attendance(request, enrollment_id):
    """تسجيل حضور طالب في حصة معينة."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # التحقق من الصلاحية (Admin أو المشرف المسؤول)
    is_authorized = request.user.is_superuser or (
        enrollment.student.supervisor and 
        enrollment.student.supervisor.user == request.user
    )
    
    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء.")
        return redirect('supervisor_dashboard')

    if enrollment.attendances.count() >= enrollment.course.sessions_count:
        messages.error(request, "عفواً، لقد اكتمل عدد حصص هذا الكورس.")
        return redirect('supervisor_dashboard')

    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        enrollment=enrollment, 
        date=today
    )

    if created:
        attendance.status = 'present'
        attendance.save()
        messages.success(request, f"تم تسجيل ✅ حضور {enrollment.student.name}.")
        
        if enrollment.student.user:
            Notification.objects.create(
                recipient=enrollment.student.user,
                title="تسجيل حضور",
                message=f"تم تسجيل حضورك في كورس {enrollment.course.name} بتاريخ {today}."
            )
    else:
        messages.warning(request, "تم تسجيل حالة لهذا الطالب اليوم مسبقاً.")

    return redirect('supervisor_dashboard')


@login_required
def mark_absence(request, enrollment_id):
    """تسجيل غياب طالب عن حصة معينة."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    is_authorized = request.user.is_superuser or (
        enrollment.student.supervisor and 
        enrollment.student.supervisor.user == request.user
    )

    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء.")
        return redirect('supervisor_dashboard')

    if enrollment.attendances.count() >= enrollment.course.sessions_count:
        messages.error(request, "عفواً، لقد اكتمل عدد حصص هذا الكورس.")
        return redirect('supervisor_dashboard')

    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        enrollment=enrollment, 
        date=today
    )

    if created:
        attendance.status = 'absent'
        attendance.save()
        messages.warning(request, f"تم تسجيل ❌ غياب {enrollment.student.name}.")
        
        if enrollment.student.user:
            Notification.objects.create(
                recipient=enrollment.student.user,
                title="تسجيل غياب",
                message=f"تم تسجيل غيابك عن كورس {enrollment.course.name} بتاريخ {today}."
            )
    else:
        messages.warning(request, "تم تسجيل حالة لهذا الطالب اليوم مسبقاً.")

    return redirect('supervisor_dashboard')


@login_required
def complete_course(request, enrollment_id):
    """إنهاء الكورس وأرشفته."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    is_authorized = request.user.is_superuser or (
        enrollment.student.supervisor and 
        enrollment.student.supervisor.user == request.user
    )

    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية.")
        return redirect('supervisor_dashboard')

    if enrollment.attendances.count() < enrollment.course.sessions_count:
        messages.error(request, "عفواً، لا يمكن إنهاء الكورس لأن الطالب لم يتم جميع الحصص المقررة بعد.")
        return redirect('supervisor_dashboard')

    enrollment.is_completed = True
    enrollment.save()
    
    messages.success(request, f"مبروك! تم إنهاء كورس {enrollment.course.name} للطالب {enrollment.student.name} وتمت أرشفته.")
    return redirect('supervisor_dashboard')
