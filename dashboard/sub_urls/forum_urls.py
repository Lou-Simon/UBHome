# Fichier : dashboard/urls/forum_urls.py
from django.urls import path
from ..views import forum 

urlpatterns = [
    path('', forum.forum_view, name='forum'),
    # Endpoint JSON pour rafraîchissement périodique des messages
    path('posts_json/', forum.forum_posts_json, name='forum_posts_json'),
    # Endpoint pour gérer les réactions
    path('toggle_reaction/', forum.toggle_reaction, name='toggle_reaction'),
    # Endpoint pour créer un sondage
    path('create_poll/', forum.create_poll, name='create_poll'),
    # Endpoint pour voter dans un sondage
    path('vote_poll/', forum.vote_poll, name='vote_poll'),
    # Endpoint pour créer un canal
    path('create_channel/', forum.create_channel, name='create_channel'),
]