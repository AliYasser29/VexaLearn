from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from core.models import Student, Teacher, Course, Enrollment
from core.forms import StudentForm, EnrollmentForm
from core.utils import is_active_manager
from core.services import create_student_with_credentials
from core.tasks import send_email_task

@login_required(login_url='login') 
def admin_panel(req, student_id=None):
    """بوابة البحث والاشتراكات للطلاب المسجلين مع تسجيل طلاب جدد."""
    if not is_active_manager(req):
        messages.error(req, "عفواً، هذه الصفحة مخصصة للمديرين الإداريين فقط بهذا الدور.")
        return redirect('chat_home')

    stats = {
        'students_count': Student.objects.count(),
        'teachers_count': Teacher.objects.count(),
        'courses_count': Course.objects.count(),
        'active_enrollments': Enrollment.objects.filter(is_completed=False).count(),
    }

    # دائماً ننشئ استمارة تسجيل طالب جديدة فارغة
    student_form = StudentForm(req.POST or None)

    search_results = None
    query = req.GET.get('q', '').strip()
    if query:
        # البحث الذكي باستخدام الاسم، أو الهاتف، أو الإيميل، أو الرقم التعريفي
        q_obj = Q(name__icontains=query) | Q(parent_phone__icontains=query) | Q(parent_email__icontains=query)
        if query.isdigit():
            q_obj |= Q(id=int(query))
            
        search_results = Student.objects.filter(q_obj).select_related('country', 'education_type', 'academic_year')

    # تسجيل طالب جديد باستخدام طبقة الخدمات (Services)
    if req.method == 'POST':
        if student_form.is_valid():
            try:
                # استدعاء طبقة الخدمات لمعالجة منطق التسجيل المعقد
                student, username, password = create_student_with_credentials(
                    student_form, req.scheme, req.get_host()
                )
                
                messages.success(req, f"تم إنشاء ملف الطالب {student.name} بنجاح. Credentials: {username} / {password} ✅")
                return redirect('add_enrollment', student_id=student.id)
            
            except Exception as e:
                messages.error(req, f"حدث خطأ أثناء الحفظ: {e}")
        else:
            messages.error(req, "يرجى التأكد من صحة البيانات المدخلة في استمارة التسجيل.")

    context = {
        'search_results': search_results,
        'query': query,
        'student_form': student_form,
        'stats': stats,
    }
    return render(req, 'core/admin_panel.html', context)


@login_required
def add_enrollment(request, student_id):
    """إضافة اشتراك جديد لطالب."""
    # التحقق من الصلاحية
    if not (request.user.is_superuser or hasattr(request.user, 'manager_profile')):
         messages.error(request, "ليس لديك صلاحية لإضافة اشتراكات.")
         return redirect('chat_home')

    student = get_object_or_404(Student, id=student_id)
    form = EnrollmentForm(request.POST or None)
    
    # فلترة الكورسات حسب بيانات الطالب
    courses_qs = Course.objects.filter(country=student.country)
    
    if student.academic_year:
        courses_qs = courses_qs.filter(academic_years=student.academic_year).distinct()
        
    form.fields['course'].queryset = courses_qs

    if request.method == 'POST':
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.save()
            
            if enrollment.teacher:
                student.teachers.add(enrollment.teacher)

            # إرسال إيميل لولي الأمر
            if student.parent_email:
                subject = f'تم تسجيل اشتراك جديد - {student.name}'
                message = f"""
                مرحباً ولي أمر الطالب/ة {student.name}،
                
                تم تسجيل الطالب بنجاح في كورس: {enrollment.course.name}
                المعلم المسؤول: {enrollment.teacher.name if enrollment.teacher else 'لم يحدد'}
                
                تاريخ البدء: {enrollment.start_date}
                السعر: {enrollment.course.price} {enrollment.course.country.currency}
                
                نتمنى له التوفيق.
                إدارة الأكاديمية
                """
                send_email_task.delay(subject, message, [student.parent_email])
                messages.info(request, f"تم إرسال إشعار الاشتراك لولي الأمر 📧")

            messages.success(request, f"تم إضافة اشتراك كورس {enrollment.course.name} للطالب {student.name} ✅")
            return redirect('add_enrollment', student_id=student.id)

    return render(request, 'core/add_enrollment.html', {'form': form, 'student': student})
