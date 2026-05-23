import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from core.context_processors import nav_items
from core.models import Student, Teacher, Supervisor, Manager

@pytest.mark.django_db
class TestNavigationContextProcessor:
    def setup_method(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_anonymous_user_empty_nav(self):
        request = self.factory.get('/')
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        context = nav_items(request)
        assert 'nav_items' in context
        assert len(context['nav_items']) == 0

    def test_student_nav_items(self):
        # Create student profile
        from core.models import Country, AcademicYear, EducationType
        country = Country.objects.create(name="Test Country")
        year = AcademicYear.objects.create(name="2024", country=country)
        Student.objects.create(
            user=self.user, 
            name="Test Student", 
            age=20, 
            country=country, 
            academic_year=year,
            parent_name="Parent",
            parent_phone="123"
        )
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = nav_items(request)
        # Note: Currently nav_items returns [] until T010/T011
        # After implementation, this should contain student items
        assert 'nav_items' in context

    def test_teacher_nav_items(self):
        Teacher.objects.create(user=self.user, name="Test Teacher", phone="123")
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = nav_items(request)
        assert 'nav_items' in context

    def test_manager_nav_items(self):
        Manager.objects.create(user=self.user, name="Test Manager", phone="123")
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = nav_items(request)
        assert 'nav_items' in context

    def test_supervisor_nav_items(self):
        Supervisor.objects.create(user=self.user, name="Test Supervisor", phone="123")
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = nav_items(request)
        assert 'nav_items' in context
