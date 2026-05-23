from django.core.management.base import BaseCommand
from core.tasks import send_email_task
from django.utils import timezone
from core.models import Enrollment
from django.conf import settings

class Command(BaseCommand):
    help = 'يرسل تذكيرات بالدفع لأولياء الأمور للكورسات الشهرية'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # 1. جلب كل الاشتراكات الشهرية
        enrollments = Enrollment.objects.filter(course__payment_type='monthly')
        
        count = 0
        for enrollment in enrollments:
            # 2. التحقق: هل اليوم هو نفس يوم الشهر الذي بدأ فيه الاشتراك؟
            # مثال: اشترك يوم 27/1، اليوم هو 27/2 -> إرسال إيميل
            if enrollment.start_date.day == today.day and enrollment.start_date != today:
                
                subject = f"تذكير بتجديد اشتراك: {enrollment.course.name}"
                message = f"""
                مرحباً السيد/ة {enrollment.student.parent_name}،
                
                نود تذكيركم بأن اشتراك الطالب ({enrollment.student.name}) في كورس ({enrollment.course.name}) 
                قد أتم شهراً جديداً اليوم.
                
                قيمة التجديد: {enrollment.course.price} {enrollment.course.country.currency}
                
                مع تحيات إدارة الأكاديمية.
                """
                
                recipient = enrollment.student.parent_email
                
                if recipient:
                    try:
                        send_email_task.delay(
                            subject,
                            message,
                            [recipient]
                        )
                        self.stdout.write(self.style.SUCCESS(f'تم إرسال إيميل لولي أمر الطالب: {enrollment.student.name}'))
                        count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'فشل الإرسال لـ {recipient}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'تم الانتهاء. تم إرسال {count} رسالة.'))