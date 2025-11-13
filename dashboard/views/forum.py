# Fichier : dashboard/views/forum.py
from django.shortcuts import render, redirect
from .auth import get_session_user_data

def forum_view(request):
    """Vue pour afficher la page du Forum."""
    user_data = get_session_user_data(request)

    if not user_data:
        return redirect('login') 
        
    context = {
        'user': user_data,
        'title': 'Forum Étudiant'
    }

    return render(request, 'forum.html', context)