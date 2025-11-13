# Fichier : dashboard/views/profile.py
from django.shortcuts import render, redirect, get_object_or_404
from .auth import get_session_user_data 
from ..models import Student # Nécessite Student pour get_object_or_404

def profile_view(request):
    """Affiche la page de profil."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        return redirect('login')
        
    student_details = get_object_or_404(Student, student_id=user_data['student_id'])
    
    return render(request, 'profile.html', {
        'student': student_details, 
        'user': user_data
    })