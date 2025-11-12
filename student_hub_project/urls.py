# Fichier : student_hub_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Garder l'interface d'administration
    path('', include('dashboard.urls')), # Lien vers les routes de l'application dashboard
]