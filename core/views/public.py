from django.shortcuts import render, get_object_or_404
from core.models import Country, Academy, Course

def landing_page(request):
    """الصفحة الرئيسية للموقع."""
    countries = Country.objects.all()
    selected_country_id = request.GET.get('country')
    
    if selected_country_id and selected_country_id.isdigit():
        selected_country_id = int(selected_country_id)
        academies = Academy.objects.filter(courses__country__id=selected_country_id).distinct()
    else:
        selected_country_id = None
        academies = Academy.objects.all()

    context = {
        'academies': academies,
        'countries': countries,
        'selected_country_id': selected_country_id,
        'academies_count': Academy.objects.count(),
        'courses_count': Course.objects.count(),
        'students_count': Course.objects.count(),  # Note: Keep original logic if standard
    }
    return render(request, 'core/landing_page.html', context)


def academy_details(request, academy_id):
    """صفحة تفاصيل الأكاديمية والكورسات."""
    academy = get_object_or_404(Academy, id=academy_id)
    courses = Course.objects.filter(academy=academy)
    
    selected_country_id = request.GET.get('country')
    if selected_country_id and selected_country_id.isdigit():
        selected_country_id = int(selected_country_id)
        courses = courses.filter(country__id=selected_country_id)
    else:
        selected_country_id = None
        
    available_country_ids = Course.objects.filter(academy=academy).values_list('country', flat=True).distinct()
    countries = Country.objects.filter(id__in=available_country_ids)
    
    return render(request, 'core/academy_details.html', {
        'academy': academy,
        'courses': courses,
        'countries': countries,
        'selected_country_id': selected_country_id,
    })


def games_page(request):
    return render(request, 'core/games_page.html')
