# Fichier : dashboard/urls.py

from django.urls import path, include 
from .views import auth, dashboard, profile 

app_name = 'dashboard' # Nécessaire pour le namespace

urlpatterns = [
    # --- AUTHENTIFICATION & CORE ---
    # La page d'accueil (/)
    path('', dashboard.dashboard_view, name='dashboard'), 
    
    # La vue de CONNEXION (C'EST LA LIGNE MANQUANTE !)
    path('login', auth.login_view, name='login'), 
    
    # La vue de DÉCONNEXION
    path('logout', auth.logout_view, name='logout'), 
    
    # La vue de PROFIL
    path('profile', profile.profile_view, name='profile'),
    
    # --- FONCTIONNALITÉS INCLUSES (sub_urls) ---
    path('calendar/', include('dashboard.sub_urls.calendar_urls')),
    path('chat/', include('dashboard.sub_urls.chat_urls')),
    path('forum/', include('dashboard.sub_urls.forum_urls')),
]