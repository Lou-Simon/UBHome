# Fichier : dashboard/urls/forum_urls.py
from django.urls import path
from ..views import forum 

urlpatterns = [
    path('', forum.forum_view, name='forum'),
    # Endpoint JSON pour rafraîchissement périodique des messages
    path('posts.json', forum.forum_posts_json, name='forum_posts_json'),
    # Endpoint pour gérer les réactions
    path('reaction/', forum.toggle_reaction, name='toggle_reaction'),
]