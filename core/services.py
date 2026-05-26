import secrets
import string
from django.contrib.auth.models import User
from core.tasks import send_email_task

def create_student_with_credentials(student_form, host_scheme, host_url):
    """
    خدمة مخصصة لإنشاء حساب مستخدم جديد للطالب وتوليد بيانات الدخول
    وإرسالها عبر البريد الإلكتروني بشكل آمن.
    """
    import re
    parent_email = student_form.cleaned_data.get('parent_email')
    raw_phone = student_form.cleaned_data.get('parent_phone', '') or ''
    # تنظيف رقم الهاتف وإبقاء الحروف اللاتينية والأرقام فقط لتجنب مشاكل تشفير أسماء المستخدمين
    clean_username = re.sub(r'[^a-zA-Z0-9]', '', raw_phone)
    if not clean_username:
        clean_username = f"student_{secrets.token_hex(4)}"

    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(10)) 
    username = clean_username
    if User.objects.filter(username=username).exists():
        username = f"{username}_{secrets.randbelow(1000)}"

    user = User.objects.create_user(username=username, password=password)
    full_name = student_form.cleaned_data['name'].split()
    if full_name:
        user.first_name = full_name[0]
        if len(full_name) > 1:
            user.last_name = full_name[-1]
    
    if parent_email:
        user.email = parent_email
    user.save()

    student = student_form.save(commit=False)
    student.user = user  
    student.save()
    
    if parent_email:
        subject = 'بيانات الدخول لمنصة VexaLearn'
        message = f"""
        مرحباً ولي أمر الطالب/ة {student.name}،
        
        تم تسجيل حساب الطالب بنجاح في المنصة.
        
        بيانات الدخول:
        اسم المستخدم: {username}
        كلمة المرور: {password}
        
        رابط المنصة: {host_scheme}://{host_url}
        """
        send_email_task.delay(subject, message, [parent_email])
        
    return student, username, password
