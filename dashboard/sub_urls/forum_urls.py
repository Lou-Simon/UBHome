# Fichier : dashboard/urls/forum_urls.py
from django.urls import path
from ..views import forum

urlpatterns = [
    path('', forum.forum_view, name='forum'),
    path('posts_json/', forum.forum_posts_json, name='forum_posts_json'),
]