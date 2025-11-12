# Fichier : dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Les noms ('dashboard', 'profile', 'login', 'logout') sont utilisés par le tag {% url %} dans le HTML.
    path('', views.dashboard_view, name='dashboard'), 
    path('profile', views.profile_view, name='profile'),
    path('login', views.login_view, name='login'), 
    path('logout', views.logout_view, name='logout'), 
    path('calendar/', views.calendar, name='calendar'),
    path('chat/', views.chat_view, name='chat'),
    path('forum/', views.forum_view, name='forum')
]
