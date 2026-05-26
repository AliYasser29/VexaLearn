from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Exists, OuterRef
from django.contrib.auth.models import User
from django.http import JsonResponse
from core.models import Student, Teacher, Enrollment, Message, DailyReport
from core.forms import DailyReportForm

@login_required(login_url='login')
def chat_room(request, user_id=None):
    """غرفة الدردشة الرئيسية مع التحقق من صلاحية مراسلة المستخدم (BOLA/IDOR Secured)."""
    current_user = request.user

    # التحقق من صلاحية الطالب للدخول للشات
    if hasattr(current_user, 'student_profile'):
        student = current_user.student_profile
        has_active_enrollment = Enrollment.objects.filter(
            student=student, 
            is_completed=False
        ).exists()

        if not has_active_enrollment:
            messages.warning(request, "عفواً ⛔، لا يمكنك الدخول للشات حالياً. يجب أن تكون مشتركاً في كورس نشط.")
            return redirect('profile_view')

    # بناء قائمة المستخدمين المتاحين للمراسلة
    q_objects = Q()

    if current_user.is_superuser or hasattr(current_user, 'manager_profile'):
        q_objects = Q(is_active=True)
    elif hasattr(current_user, 'supervisor_profile'):
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

    users_list = User.objects.filter(q_objects).filter(is_active=True)

    if not current_user.is_superuser:
        active_admins = User.objects.filter(is_superuser=True).filter(
            Q(sent_messages__receiver=current_user) | 
            Q(received_messages__sender=current_user)
        )
        users_list = users_list | active_admins

    unread_subquery = Message.objects.filter(
        sender=OuterRef('pk'), 
        receiver=current_user, 
        is_read=False
    )

    users_list = users_list.exclude(id=current_user.id)\
        .annotate(has_unread_messages=Exists(unread_subquery))\
        .distinct()

    final_users_list = []
    for u in users_list:
        u.display_name = u.first_name + " " + u.last_name if u.first_name else u.username
        u.role_label = 'مستخدم'
        u.role_icon = 'fas fa-user'

        if hasattr(u, 'manager_profile'):
            u.display_name = u.manager_profile.name
            u.role_label = 'مدير إداري'
            u.role_icon = 'fas fa-user-tie'
        elif hasattr(u, 'supervisor_profile'):
            u.display_name = u.supervisor_profile.name
            u.role_label = 'مشرف'
            u.role_icon = 'fas fa-user-shield'
        elif hasattr(u, 'teacher_profile'):
            u.display_name = u.teacher_profile.name
            u.role_label = 'معلم'
            u.role_icon = 'fas fa-chalkboard-teacher'
        elif hasattr(u, 'student_profile'):
            u.display_name = u.student_profile.name
            u.role_label = 'طالب'
            u.role_icon = 'fas fa-user-graduate'
        elif u.is_superuser:
            u.role_label = 'Admin'
            u.role_icon = 'fas fa-cogs'
        
        u.has_unread = getattr(u, 'has_unread_messages', False)
        final_users_list.append(u)
    
    users_list = final_users_list 

    selected_user = None
    messages_list = []
    report_form = None
    already_reported_today = False
    target_student_id = None

    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        
        selected_user.display_name = selected_user.username
        selected_user.role_label = 'مستخدم'
        if hasattr(selected_user, 'manager_profile'):
            selected_user.display_name = selected_user.manager_profile.name
        elif hasattr(selected_user, 'supervisor_profile'):
            selected_user.display_name = selected_user.supervisor_profile.name
        elif hasattr(selected_user, 'teacher_profile'):
            selected_user.display_name = selected_user.teacher_profile.name
        elif hasattr(selected_user, 'student_profile'):
            selected_user.display_name = selected_user.student_profile.name
        elif selected_user.is_superuser:
            selected_user.display_name = "Admin"

        if hasattr(current_user, 'teacher_profile') and hasattr(selected_user, 'student_profile'):
            target_student = selected_user.student_profile
            target_student_id = target_student.id
            today = timezone.now().date()
            already_reported_today = DailyReport.objects.filter(
                teacher=current_user.teacher_profile,
                student=target_student,
                date=today
            ).exists()
            report_form = DailyReportForm()

        # [تأمين الشات ضد ثغرات BOLA/IDOR]
        is_chat_allowed = False
        for u in users_list:
            if u.id == selected_user.id:
                is_chat_allowed = True
                break
                
        if not is_chat_allowed:
            messages.error(request, "غير مصرح لك بفتح محادثة مع هذا المستخدم.")
            return redirect('chat_home')

        Message.objects.filter(sender=selected_user, receiver=current_user, is_read=False).update(is_read=True)

        messages_list = Message.objects.filter(
            Q(sender=current_user, receiver=selected_user) |
            Q(sender=selected_user, receiver=current_user)
        ).order_by('timestamp')

        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                Message.objects.create(sender=current_user, receiver=selected_user, content=content)
                return redirect('chat_room', user_id=user_id)

    context = {
        'users_list': users_list,
        'selected_user': selected_user,
        'chat_messages': messages_list,
        'current_user': current_user,
        'report_form': report_form,
        'already_reported_today': already_reported_today,
        'target_student_id': target_student_id,
    }
    return render(request, 'core/chat.html', context)


@login_required
def check_new_messages(request):
    """API للتحقق من الرسائل الجديدة دون تحديث الصفحة."""
    latest_message = Message.objects.filter(
        receiver=request.user, 
        is_read=False
    ).order_by('-timestamp').first()

    if latest_message:
        return JsonResponse({
            'has_new': True,
            'sender': latest_message.sender.first_name or latest_message.sender.username,
            'content': latest_message.content[:50],
            'msg_id': latest_message.id
        })
    else:
        return JsonResponse({'has_new': False})


@login_required
def submit_daily_report(request, student_id):
    """رفع التقرير اليومي للطالب من قبل المعلم."""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "عفواً، هذه الميزة للمعلمين فقط.")
        return redirect('chat_home')

    student = get_object_or_404(Student, id=student_id)
    teacher = request.user.teacher_profile
    today = timezone.now().date()

    # التحقق من وجود علاقة أكاديمية نشطة لتجنب ثغرة IDOR
    is_my_student = Enrollment.objects.filter(student=student, teacher=teacher, is_completed=False).exists()
    if not is_my_student and not request.user.is_superuser:
        messages.error(request, "عفواً، لا يمكنك رفع تقارير لطلاب ليسوا في مجموعاتك الدراسية النشطة.")
        return redirect('chat_home')

    if DailyReport.objects.filter(student=student, teacher=teacher, date=today).exists():
        messages.warning(request, "لقد قمت برفع تقرير لهذا الطالب اليوم بالفعل.")
        return redirect('chat_room', user_id=student.user.id)

    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = student
            report.teacher = teacher
            report.save()
            messages.success(request, "تم رفع التقرير اليومي بنجاح ✅")
            return redirect('chat_room', user_id=student.user.id)
    
    return redirect('chat_room', user_id=student.user.id)


@login_required
def monitor_student_chat(request, student_id):
    """مراقبة شات الطالب (للمشرفين والمدراء)."""
    student = get_object_or_404(Student, id=student_id)
    
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
    elif hasattr(request.user, 'supervisor_profile') and student.supervisor == request.user.supervisor_profile:
        is_authorized = True
    elif hasattr(request.user, 'manager_profile'):
        is_authorized = True
        
    if not is_authorized:
        messages.error(request, "ليس لديك صلاحية للاطلاع على بيانات هذا الطالب.")
        return redirect('supervisor_dashboard')

    teachers = student.teachers.all()
    supervisor = student.supervisor
    
    selected_teacher = None
    selected_supervisor = None 
    chat_messages = []

    teacher_id = request.GET.get('teacher_id')
    supervisor_id = request.GET.get('supervisor_id')

    if teacher_id:
        selected_teacher = get_object_or_404(Teacher, id=teacher_id)
        if student.user and selected_teacher.user:
            chat_messages = Message.objects.filter(
                (Q(sender=student.user, receiver=selected_teacher.user) |
                 Q(sender=selected_teacher.user, receiver=student.user))
            ).order_by('timestamp')
            
    elif supervisor_id and supervisor:
        if int(supervisor_id) == supervisor.id:
            selected_supervisor = supervisor
            if student.user and selected_supervisor.user:
                chat_messages = Message.objects.filter(
                    (Q(sender=student.user, receiver=selected_supervisor.user) |
                     Q(sender=selected_supervisor.user, receiver=student.user))
                ).order_by('timestamp')

    student_reports = DailyReport.objects.filter(student=student).select_related('teacher').order_by('-date')

    context = {
        'student': student,
        'teachers': teachers,
        'supervisor': supervisor,
        'selected_teacher': selected_teacher,
        'selected_supervisor': selected_supervisor,
        'chat_messages': chat_messages,
        'student_reports': student_reports,
    }
    return render(request, 'core/monitor_chat.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def student_full_chat_log(request, student_id):
    """سجل المحادثات الكامل للطالب (للمدير العام)."""
    student = get_object_or_404(Student, id=student_id)
    teachers = student.teachers.all()
    student_reports = DailyReport.objects.filter(student=student).order_by('-date')

    selected_teacher = None
    chat_messages = []

    teacher_id = request.GET.get('teacher_id')
    
    if teacher_id:
        try:
            selected_teacher = Teacher.objects.get(id=teacher_id)
            if student.user and selected_teacher.user:
                chat_messages = Message.objects.filter(
                    Q(sender=student.user, receiver=selected_teacher.user) | 
                    Q(sender=selected_teacher.user, receiver=student.user)
                ).order_by('timestamp')
        except Teacher.DoesNotExist:
            selected_teacher = None

    context = {
        'student': student,
        'teachers': teachers,
        'student_reports': student_reports,
        'selected_teacher': selected_teacher,
        'chat_messages': chat_messages,
    }
    
    return render(request, 'core/student_full_chat_log.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def universal_chat_monitor(request):
    """مراقبة شاملة لكل المحادثات في النظام (God Mode)."""
    all_users = User.objects.filter(is_active=True).select_related(
        'student_profile', 'teacher_profile', 'supervisor_profile', 'manager_profile'
    )
    
    users_data = []
    for u in all_users:
        role = "مستخدم"
        name = u.username 
        if hasattr(u, 'student_profile'):
            role = "طالب"
            name = u.student_profile.name
        elif hasattr(u, 'teacher_profile'):
            role = "معلم"
            name = u.teacher_profile.name
        elif hasattr(u, 'supervisor_profile'):
            role = "مشرف"
            name = u.supervisor_profile.name
        elif hasattr(u, 'manager_profile'):
            role = "مدير"
            name = u.manager_profile.name
        elif u.is_superuser:
            role = "Admin"
            
        users_data.append({
            'id': u.id,
            'name': name,
            'role': role,
            'username': u.username
        })
    
    users_data.sort(key=lambda x: x['name'])

    user1_id = request.GET.get('user1')
    user2_id = request.GET.get('user2')
    
    chat_messages = []
    daily_reports = []
    show_reports_panel = False
    
    user1_obj = None
    user2_obj = None

    if user1_id and user2_id:
        try:
            user1_obj = User.objects.get(id=user1_id)
            user2_obj = User.objects.get(id=user2_id)
            
            chat_messages = Message.objects.filter(
                (Q(sender=user1_obj, receiver=user2_obj) | 
                 Q(sender=user2_obj, receiver=user1_obj))
            ).order_by('timestamp')

            student_profile = None
            teacher_profile = None

            if hasattr(user1_obj, 'student_profile') and hasattr(user2_obj, 'teacher_profile'):
                student_profile = user1_obj.student_profile
                teacher_profile = user2_obj.teacher_profile
            
            elif hasattr(user1_obj, 'teacher_profile') and hasattr(user2_obj, 'student_profile'):
                teacher_profile = user1_obj.teacher_profile
                student_profile = user2_obj.student_profile

            if student_profile and teacher_profile:
                show_reports_panel = True
                daily_reports = DailyReport.objects.filter(
                    student=student_profile,
                    teacher=teacher_profile
                ).order_by('-date')

        except User.DoesNotExist:
            pass

    context = {
        'users_data': users_data,
        'chat_messages': chat_messages,
        'daily_reports': daily_reports,
        'show_reports_panel': show_reports_panel,
        'user1_id': int(user1_id) if user1_id else None,
        'user2_id': int(user2_id) if user2_id else None,
        'user1_obj': user1_obj,
        'user2_obj': user2_obj,
    }
    return render(request, 'core/universal_chat_monitor.html', context)
