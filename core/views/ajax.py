from django.shortcuts import render
from django.http import JsonResponse
from core.models import Teacher, Course, EducationType, AcademicYear

def load_teachers(request):
    """API لفلترة المعلمين حسب الكورس المختار (AJAX)."""
    course_id = request.GET.get('course_id')
    teachers = Teacher.objects.none()
    
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            if course.subject:
                teachers = course.subject.teachers.all()
        except:
            pass
            
    return render(request, 'core/teacher_dropdown_list_options.html', {'teachers': teachers})


def load_education_types(request):
    country_id = request.GET.get('country_id')
    if country_id:
        types = EducationType.objects.filter(country_id=country_id).values('id', 'name')
        return JsonResponse(list(types), safe=False)
    return JsonResponse([], safe=False)

def load_academic_years(request):
    country_id = request.GET.get('country_id')
    if country_id:
        years = AcademicYear.objects.filter(country_id=country_id).values('id', 'name')
        return JsonResponse(list(years), safe=False)
    return JsonResponse([], safe=False)
