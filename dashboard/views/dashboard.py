# Fichier : dashboard/views/dashboard.py

from django.shortcuts import render, redirect
from django.utils import timezone 
from datetime import timedelta
# Assurez-vous d'importer vos modèles/utilitaires
from ..models import Student, Event, Email, ForumPost
from .auth import get_session_user_data 

def dashboard_view(request):
    """Affiche le Tableau de Bord avec le calendrier du jour, les derniers emails et les posts du forum."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        return redirect('dashboard:login')
    
    # --- 1. Récupérer l'objet Student et les données associées ---
    try:
        student = Student.objects.get(student_id=user_data['student_id'])
    except Student.DoesNotExist:
        return redirect('dashboard:login')

    # --- 2. DONNÉES DU CALENDRIER (Aujourd'hui seulement) ---
    
    current_date = timezone.localdate()
    enrolled_course_ids = student.enrolled_courses.values_list('id', flat=True)

    # Événements du jour
    today_events = Event.objects.select_related('course').filter(
        course_id__in=enrolled_course_ids,
        start_time__date=current_date
    ).order_by('start_time')
    
    # Constantes pour le calcul des pixels
    PX_PER_HOUR = 100
    START_HOUR_CALENDAR = 8 

    # Calcul des styles pour les événements du jour
    styled_events = []
    color_map = {0: 'teal', 1: 'indigo', 2: 'primary', 3: 'red'}
    
    for event in today_events:
        local_start_time = timezone.localtime(event.start_time)
        local_end_time = timezone.localtime(event.end_time)

        # Calcul du TOP (position)
        start_hour = local_start_time.hour
        start_minute = local_start_time.minute
        hour_offset = (start_hour - START_HOUR_CALENDAR) * PX_PER_HOUR
        minute_offset = int((start_minute / 60) * PX_PER_HOUR)
        event.total_start_offset = max(0, hour_offset + minute_offset)
        
        # Calcul de la HAUTEUR
        duration = (local_end_time - local_start_time).total_seconds() / 3600
        event.height = int(duration * PX_PER_HOUR)
        
        # Détermination de la COULEUR
        color_key = event.course.id % 4 
        event.color_code = color_map.get(color_key, 'primary')
        
        event.local_start_time = local_start_time
        event.local_end_time = local_end_time
        styled_events.append(event)
    
    # Création du pseudo 'week_days' pour le template (contient juste le jour d'aujourd'hui)
    today_data = {
        'day_name': 'Aujourd\'hui',
        'date': current_date,
        'events': styled_events
    }

    # --- 3. DONNÉES DES MAILS ET FORUM (Résumé) ---
    
    # 5 derniers emails non lus
    unread_emails = Email.objects.filter(
        recipient=student,
        is_read=False
    ).order_by('-sent_at')[:5]
    
    # 5 derniers posts dans les canaux de l'étudiant (ou tous, selon la logique)
    recent_posts = ForumPost.objects.select_related('author', 'channel').order_by('-posted_at')[:5]

    # --- 4. Contexte pour le Template ---
    
    context = {
        'user': user_data,
        'hours': range(8, 18), # Nécessaire pour les graduations du calendrier du jour
        'today_data': today_data, # Contient les événements stylisés d'aujourd'hui
        'unread_emails': unread_emails,
        'recent_posts': recent_posts,
    }
        
    return render(request, 'dashboard.html', context)