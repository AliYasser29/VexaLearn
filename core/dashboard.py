<<<<<<< HEAD
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Country, Enrollment, Student, Course, Teacher, AcademicYear, Academy

def dashboard_callback(request, context):
    kpi_data = []
    
    # قراءة فلتر الفترة من GET param
    try:
        period = int(request.GET.get('income_period', 30))
    except (TypeError, ValueError):
        period = 30
    if period not in (7, 30, 90):
        period = 30

    # تحديد نقطة البداية للفترة
    today = timezone.now().date()
    since = today - timedelta(days=period)

    # 1. الطلاب
    total_students = Student.objects.filter(enrollment__start_date__gte=since).distinct().count()
    kpi_data.append({
        "title": "الطلاب",
        "metric": str(total_students),
        "link": reverse('admin:core_student_changelist'),
        "footer": f"الطلاب الجدد خلال آخر {period} يوم",
        "icon": "school",
    })

    # 2. الكورسات
    total_courses = Course.objects.filter(enrollment__start_date__gte=since).distinct().count()
    kpi_data.append({
        "title": "الكورسات",
        "metric": str(total_courses),
        "link": reverse('admin:core_course_changelist'),
        "footer": f"الكورسات النشطة خلال آخر {period} يوم",
        "icon": "library_books",
    })

    # 3. المعلمون
    total_teachers = Teacher.objects.filter(student__enrollment__start_date__gte=since).distinct().count()
    kpi_data.append({
        "title": "المعلمون",
        "metric": str(total_teachers),
        "link": reverse('admin:core_teacher_changelist'),
        "footer": f"المعلمون النشطون خلال آخر {period} يوم",
        "icon": "person",
    })

    # 4. الاشتراكات النشطة
    active_enrollments = Enrollment.objects.filter(start_date__gte=since, is_completed=False).count()
    kpi_data.append({
        "title": "الاشتراكات النشطة",
        "metric": str(active_enrollments),
        "footer": f"غير المكتملة (آخر {period} يوم)",
        "icon": "pending_actions",
    })
    
    # ===== الإحصائيات حسب الدول =====
    
    # 5. جلب الدول
    countries = Country.objects.annotate(student_count=Count('student'))

    # 6. إضافة بطاقة لكل دولة
    if countries.exists():
        for country in countries:
            # حساب الأرباح في الفترة لهذه الدولة فقط
            revenue_data = Enrollment.objects.filter(course__country=country, start_date__gte=since).aggregate(
                total=Sum('course__price')
            )
            revenue = revenue_data['total'] if revenue_data['total'] is not None else 0
            
            # عدد الطلاب لهذه الدولة في الفترة
            student_count_period = Student.objects.filter(country=country, enrollment__start_date__gte=since).distinct().count()

            kpi_data.append({
                "title": f"إيرادات {country.name}",
                "metric": f"{revenue} {country.currency}",
                "footer": f"عدد الطلاب: {student_count_period} (آخر {period} يوم)",
                "icon": "monetization_on",
            })
    
    # 7. السنوات الدراسية
    academic_years = AcademicYear.objects.filter(student__enrollment__start_date__gte=since).distinct().count()
    kpi_data.append({
        "title": "السنوات الدراسية",
        "metric": str(academic_years),
        "link": reverse('admin:core_academicyear_changelist'),
        "footer": f"سنوات بها نشاط خلال آخر {period} يوم",
        "icon": "calendar_today",
    })

    # 8. إحصائيات الأكاديميات (تمت الإضافة)
    academies = Academy.objects.all()

    if academies.exists():
        for academy in academies:
            # حساب عدد الطلاب المسجلين في كورسات تابعة لهذه الأكاديمية خلال الفترة المحددة
            student_count = Student.objects.filter(
                enrollment__course__academy=academy,
                enrollment__start_date__gte=since
            ).distinct().count()

            kpi_data.append({
                "title": f"طلاب {academy.name}",
                "metric": str(student_count),
                "footer": f"المسجلين خلال آخر {period} يوم",
                "icon": "domain", 
            })

    # تحديث البيانات
    context.update({
        "kpi": kpi_data,
        "income_period": period,
    })

=======
from django.db.models import Sum, Count
from .models import Country, Enrollment

def dashboard_callback(request, context):
    kpi_data = []

    # 1. جلب الدول مع عدد الطلاب
    countries = Country.objects.annotate(student_count=Count('student'))

    # 2. التحقق: هل توجد دول؟
    if countries.exists():
        for country in countries:
            # حساب الأرباح
            revenue_data = Enrollment.objects.filter(course__country=country).aggregate(
                total=Sum('course__price')
            )
            
            # حماية من القيم الفارغة (إذا لم يكن هناك اشتراكات)
            revenue = revenue_data['total'] if revenue_data['total'] is not None else 0

            # إضافة البطاقة
            kpi_data.append({
                "title": country.name,
                "metric": f"{revenue} {country.currency}",
                "footer": f"عدد الطلاب: {country.student_count}",
                "icon": "public", # أيقونة الكرة الأرضية
            })
    else:
        # 3. إذا لم تكن هناك بيانات، اعرض بطاقة ترحيبية حتى لا تظهر الصفحة فارغة
        kpi_data.append({
            "title": "مرحباً بك",
            "metric": "النظام يعمل",
            "footer": "قم بإضافة دول وطلاب لتظهر الإحصائيات",
            "icon": "check_circle",
        })

    # تحديث البيانات
    context.update({
        "kpi": kpi_data,
    })

>>>>>>> d5830918c0c5f5125220644ff97bb92f7726c7f7
    return context