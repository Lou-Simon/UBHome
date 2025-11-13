# Fichier : student_hub_project/urls.py

from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # AJOUT du namespace='dashboard'
    path('', include('dashboard.urls', namespace='dashboard')), 
]

# Service des médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)