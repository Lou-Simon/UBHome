# Fichier : dashboard/urls/chat_urls.py
from django.urls import path
from ..views import chat 

urlpatterns = [
    path('', chat.chat_view, name='chat'),
]