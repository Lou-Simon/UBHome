# Fichier : student_hub_project/urls.py

from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # AJOUT du namespace='dashboard'
    path('', include('dashboard.urls', namespace='dashboard')), 
]