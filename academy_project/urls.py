"""
URL configuration for academy_project project.
"""
from django.contrib import admin
from django.urls import path, include

# استيراد المكتبات اللازمة للملفات الثابتة (التصميم والصور)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('quiz/', include('quiz.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)