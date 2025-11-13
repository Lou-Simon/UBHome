# Fichier : dashboard/views/calendar.py
from django.shortcuts import render, redirect
from .auth import get_session_user_data

def calendar(request):
    """Vue pour afficher la page du calendrier."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        return redirect('login')
        
    context = {
        'user': user_data,
        'title': 'Calendrier'
    }
    
    return render(request, 'calendar.html', context)