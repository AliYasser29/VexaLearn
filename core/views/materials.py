from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Course, CourseMaterial, Enrollment
from core.forms import MaterialForm

@login_required
def upload_material(request):
    """رفع الملفات التعليمية من قبل المعلم."""
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "هذه الصفحة للمعلمين فقط.")
        return redirect('profile_view')

    teacher = request.user.teacher_profile
    
    if request.method == 'POST':
        form = MaterialForm(teacher, request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.teacher = teacher
            material.save()
            messages.success(request, f"تم رفع الملف '{material.title}' بنجاح ✅")
            return redirect('profile_view')
    else:
        form = MaterialForm(teacher)

    return render(request, 'core/upload_material.html', {'form': form})


@login_required
def course_materials(request, course_id):
    """عرض المواد التعليمية للكورس."""
    course = get_object_or_404(Course, id=course_id)
    
    # التحقق: هل الطالب مشترك؟
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        
        enrollment = Enrollment.objects.filter(student=student, course=course).first()
        
        if not enrollment:
            messages.error(request, "أنت غير مشترك في هذا الكورس.")
            return redirect('profile_view')
        
        my_teacher = enrollment.teacher
        
        if not my_teacher:
            materials = []
            messages.warning(request, "لم يتم تحديد معلم لك في هذا الكورس بعد.")
        else:
            materials = CourseMaterial.objects.filter(
                course=course, 
                teacher=my_teacher
            ).order_by('-created_at')
            
    # للمعلم
    elif hasattr(request.user, 'teacher_profile'):
        teacher = request.user.teacher_profile
        materials = CourseMaterial.objects.filter(course=course, teacher=teacher).order_by('-created_at')
        my_teacher = teacher
            
    # للمدير والمشرف
    elif request.user.is_superuser or hasattr(request.user, 'manager_profile'):
        materials = CourseMaterial.objects.filter(course=course).order_by('-created_at')
        my_teacher = None
    else:
        return redirect('profile_view')

    return render(request, 'core/course_materials.html', {
        'course': course, 
        'materials': materials,
        'teacher': my_teacher
    })
