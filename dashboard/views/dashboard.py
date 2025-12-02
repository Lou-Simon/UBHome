# Fichier : dashboard/views/dashboard.py

from django.shortcuts import render, redirect
from django.utils import timezone 
from datetime import timedelta
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
    enrolled_course_ids = student.courses.values_list('id', flat=True)

    # Événements du jour
    today_events = Event.objects.select_related('course').filter(
        course_id__in=enrolled_course_ids,
        start_time__date=current_date
    ).order_by('start_time')
    
    # Constantes pour le calcul des pixels
    PX_PER_HOUR = 60  # CHANGÉ : 60px par heure (pour correspondre au HTML)
    START_HOUR_CALENDAR = 8  # Le calendrier commence à 8h00

    # Calcul des styles pour les événements du jour
    styled_events = []
    color_map = {0: 'teal', 1: 'indigo', 2: 'primary', 3: 'red'}
    
    for event in today_events:
        local_start_time = timezone.localtime(event.start_time)
        local_end_time = timezone.localtime(event.end_time)

        # Calcul du TOP (position)
        start_hour = local_start_time.hour
        start_minute = local_start_time.minute
        
        # CORRECTION : Vérifier que l'événement est bien dans la plage 8h-18h
        if start_hour < START_HOUR_CALENDAR:
            # L'événement commence avant 8h, on le positionne à 0
            hour_offset = 0
            minute_offset = 0
        else:
            hour_offset = (start_hour - START_HOUR_CALENDAR) * PX_PER_HOUR
            minute_offset = int((start_minute / 60) * PX_PER_HOUR)
        
        event.total_start_offset = hour_offset + minute_offset
        
        # Calcul de la HAUTEUR
        duration_seconds = (local_end_time - local_start_time).total_seconds()
        duration_hours = duration_seconds / 3600
        event.height = int(duration_hours * PX_PER_HOUR)
        
        # AJOUT : S'assurer qu'il y a une hauteur minimum
        if event.height < 20:
            event.height = 20
        
        # Détermination de la COULEUR
        color_key = event.course.id % 4 
        event.color_code = color_map.get(color_key, 'primary')
        
        # AJOUT : Informations supplémentaires pour le debug
        event.local_start_time = local_start_time
        event.local_end_time = local_end_time
        event.display_name = event.course.name
        event.location = event.location if hasattr(event, 'location') else 'Salle non définie'
        
        styled_events.append(event)
    
    # DEBUG : Afficher dans la console les événements trouvés
    print(f"=== DEBUG DASHBOARD ===")
    print(f"Date actuelle : {current_date}")
    print(f"Nombre d'événements trouvés : {len(styled_events)}")
    for evt in styled_events:
        print(f"  - {evt.course.name}: {evt.local_start_time.strftime('%H:%M')} - {evt.local_end_time.strftime('%H:%M')}")
        print(f"    Position: {evt.total_start_offset}px, Hauteur: {evt.height}px")
    print(f"=====================")
    
    # Création du pseudo 'week_days' pour le template
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
    
    # 5 derniers posts dans les canaux de l'étudiant
    recent_posts = ForumPost.objects.select_related('author', 'channel').order_by('-posted_at')[:5]

    # --- 4. Contexte pour le Template ---
    
    context = {
        'user': user_data,
        'hours': range(8, 18),  # Graduations de 8h à 17h
        'today_data': today_data,
        'unread_emails': unread_emails,
        'recent_posts': recent_posts,
    }
        
    return render(request, 'dashboard.html', context)