# Fichier : dashboard/urls/forum_urls.py
from django.urls import path
from ..views import forum 

urlpatterns = [
    path('', forum.forum_view, name='forum'),
]