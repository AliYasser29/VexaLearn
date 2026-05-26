from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Student, Country, EducationType, AcademicYear, Manager

class SoftDeleteTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Egypt", currency="EGP")
        self.edu_type = EducationType.objects.create(name="General", country=self.country)
        self.acad_year = AcademicYear.objects.create(name="First Year", country=self.country)
        
        self.user = User.objects.create_user(username='test_student', password='password123')
        self.student = Student.objects.create(
            user=self.user,
            name='Test Student',
            age=15,
            country=self.country,
            education_type=self.edu_type,
            academic_year=self.acad_year,
            parent_name='Parent',
            parent_phone='010000000',
            parent_email='parent@test.com'
        )

    def test_soft_delete_preserves_object(self):
        # Trigger soft delete
        self.student.delete()
        
        # Verify it is hidden from default manager
        hidden = Student.objects.filter(id=self.student.id).exists()
        self.assertFalse(hidden)
        
        # Verify it persists physically via all_objects
        persists = Student.all_objects.filter(id=self.student.id).exists()
        self.assertTrue(persists)
        
        # Verify linked user login status is disabled
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

class AdminPanelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name="Egypt", currency="EGP")
        self.edu_type = EducationType.objects.create(name="General", country=self.country)
        self.acad_year = AcademicYear.objects.create(name="First Year", country=self.country)
        
        # Admin user
        self.admin_user = User.objects.create_user(username='admin_user', password='password123')
        Manager.objects.create(user=self.admin_user, name='Admin Manager', phone='011', email='m@m.com')
        
    def test_admin_panel_displays_generated_credentials(self):
        self.client.login(username='admin_user', password='password123')
        
        response = self.client.post(reverse('admin_panel'), {
            'add_student': '1',
            'name': 'New Backup Student',
            'age': 16,
            'country': self.country.id,
            'education_type': self.edu_type.id,
            'academic_year': self.acad_year.id,
            'parent_name': 'Parent Name',
            'parent_phone': '01122334455',
            'parent_email': 'parent_new@test.com'
        }, follow=True)
        
        # Ensure that the flash message generated properly
        messages = list(response.context.get('messages'))
        found_message = False
        for msg in messages:
            if 'Credentials:' in str(msg):
                found_message = True
                break
                
        self.assertTrue(found_message)

class EmailConversionTests(TestCase):
    def test_convert_plain_text_to_html_formatting(self):
        from core.tasks import convert_plain_text_to_html
        
        subject = "مرحباً بك في الأكاديمية"
        message = """مرحباً أحمد،
        
        تم تسجيل حساب الطالب بنجاح في المنصة.
        
        بيانات الدخول:
        اسم المستخدم: student_user
        كلمة المرور: pass_secure
        
        رابط المنصة: https://vexalearn.cloud/dashboard
        """
        
        html_content = convert_plain_text_to_html(subject, message)
        
        # Verify subject is present
        self.assertIn("مرحباً بك في الأكاديمية", html_content)
        # Verify greeting is styled
        self.assertIn("مرحباً أحمد", html_content)
        # Verify credential formatting wraps in code tags
        self.assertIn("student_user", html_content)
        self.assertIn("pass_secure", html_content)
        self.assertIn("code style=", html_content)
        # Verify action button is generated for URL
        self.assertIn("https://vexalearn.cloud/dashboard", html_content)
        # Verify RTL layout direction is present
        self.assertIn('dir="rtl"', html_content)
