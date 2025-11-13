# Fichier : dashboard/views/chat.py
from django.shortcuts import render, redirect
from .auth import get_session_user_data

def chat_view(request):
    """Vue pour afficher la page de chat/emails."""
    user_data = get_session_user_data(request)

    if not user_data:
        return redirect('login')
        
    context = {
        'user': user_data,
        'title': 'Chat et Emails'
    }

    return render(request, 'chat.html', context)