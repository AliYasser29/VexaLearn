import threading
from django.core.mail import send_mail
from django.conf import settings

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.html_content,
                settings.EMAIL_HOST_USER,
                self.recipient_list,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_mail_async(subject, message, recipient_list):
    """
    دالة مساعدة لإرسال الإيميل في الخلفية دون تعطيل المستخدم
    """
    EmailThread(subject, message, recipient_list).start()