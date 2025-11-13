# Fichier : dashboard/views/dashboard.py

from django.shortcuts import render, redirect
from .auth import get_session_user_data # Import de l'utilitaire

def dashboard_view(request):
    """Affiche le Tableau de Bord."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        # CORRECTION : Ajout du namespace 'dashboard:'
        return redirect('dashboard:login') 
        
    return render(request, 'dashboard.html', {'user': user_data})