from django.shortcuts import render, redirect
from django.utils import timezone 
from datetime import timedelta
# Assurez-vous que ces imports correspondent à votre structure de projet
from ..models import Student, Event 
from .auth import get_session_user_data 

def calendar(request):
    """Vue pour afficher la page du calendrier, y compris la navigation hebdomadaire et le filtrage des événements de l'étudiant."""
    
    user_data = get_session_user_data(request)
    if not user_data:
        return redirect('dashboard:login')
    
    # 1. Récupérer l'objet Student
    try:
        student = Student.objects.get(student_id=user_data['student_id'])
    except Student.DoesNotExist:
        # Rediriger vers la connexion si l'étudiant n'est pas trouvé
        return redirect('dashboard:login') 

    # --- 2. Détermination de la semaine courante ---
    date_str = request.GET.get('date')
    
    # Déterminer la date de référence (aujourd'hui ou celle passée en paramètre)
    if date_str:
        try:
            # Conversion de la chaîne en objet date (sans fuseau horaire ici)
            current_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            # FIX 1: Suppression du .date() redondant qui provoquait l'AttributeError
            current_date = timezone.localdate()
    else:
        # FIX 1: Suppression du .date() redondant qui provoquait l'AttributeError
        current_date = timezone.localdate() 
    
    # Trouver le Lundi de la semaine de `current_date` (Lundi = 0)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_displayed_week = start_of_week + timedelta(days=4) # Fin affichée (Vendredi)

    # Déterminer la fin de la plage de requête (Dimanche pour couvrir tous les événements de la semaine)
    end_of_query_week = start_of_week + timedelta(days=6)

    # --- 3. Récupération et organisation des événements ---
    
    # On remplace 'enrolled_courses' par 'courses'
    enrolled_course_ids = student.courses.values_list('id', flat=True)

    all_events = Event.objects.select_related('course').filter(
        course_id__in=enrolled_course_ids,
        # Utiliser local_start_time__date__gte et local_start_time__date__lte est plus robuste 
        # en utilisant __date pour extraire la date du champ DateTimeField.
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_query_week # On interroge jusqu'à dimanche inclus
    ).order_by('start_time')
    
    events_by_day = {}
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'] 
    
    # Initialisation de la structure pour les 5 jours affichés (0=Lundi à 4=Vendredi)
    for i in range(5): 
        date = start_of_week + timedelta(days=i)
        events_by_day[i] = {
            'day_name': day_names[i],
            'date': date,
            'events': []
        }
    
    # Constantes pour le calcul des pixels
    PX_PER_HOUR = 100
    START_HOUR_CALENDAR = 8 # La grille commence à 8h00

    # Remplissage des événements par jour et calcul des propriétés de style (pixels, couleur)
    for event in all_events:
        # Les champs 'start_time' et 'end_time' sont des objets datetime Aware.
        # timezone.localtime les convertit dans le fuseau horaire local (celui de l'utilisateur/serveur)
        local_start_time = timezone.localtime(event.start_time)
        local_end_time = timezone.localtime(event.end_time)

        # Calcul de l'index du jour par rapport au Lundi de la semaine affichée
        day_index = (local_start_time.date() - start_of_week).days
        
        if 0 <= day_index < 5: # Lundi (0) à Vendredi (4)
            
            # --- CALCUL DU TOP (POSITION) EN PIXELS ---
            start_hour = local_start_time.hour
            start_minute = local_start_time.minute
            
            # Calcule le décalage en minutes depuis 8h00, puis le convertit en pixels
            # 100px par heure. (Heure - 8) * 100 + (Minutes / 60) * 100
            hour_offset = (start_hour - START_HOUR_CALENDAR) * PX_PER_HOUR
            minute_offset = int((start_minute / 60) * PX_PER_HOUR)
            
            event.total_start_offset = max(0, hour_offset + minute_offset) # S'assure que le top n'est pas négatif
            
            # --- CALCUL DE LA HAUTEUR EN PIXELS ---
            duration = (local_end_time - local_start_time).total_seconds() / 3600
            event.height = int(duration * PX_PER_HOUR)
            
            # --- DÉTERMINATION DE LA COULEUR ---
            color_map = {0: 'teal', 1: 'indigo', 2: 'primary', 3: 'red'}
            
            # Utiliser l'ID du cours pour une couleur stable
            color_key = event.course.id % 4 
            event.color_code = color_map.get(color_key, 'primary')
            
            # Ajout des dates/heures locales dans l'objet event pour le template
            event.local_start_time = local_start_time
            event.local_end_time = local_end_time
            
            events_by_day[day_index]['events'].append(event)


    # --- 4. Contexte pour le Template ---
    
    prev_week = start_of_week - timedelta(weeks=1)
    next_week = start_of_week + timedelta(weeks=1)
    
    # Création de la liste finale des 5 jours
    week_days_list = [events_by_day[i] for i in range(5)] 
    
    current_week_label = f"Semaine du {start_of_week.strftime('%d %B')} au {end_of_displayed_week.strftime('%d %B %Y')}"
    
    hours = range(8, 18) # 8, 9, 10, ..., 17 pour les graduations
        
    context = {
        'user': user_data,
        'title': 'Calendrier',
        'week_days': week_days_list, 
        'current_week_label': current_week_label,
        'prev_week_date': prev_week.strftime('%Y-%m-%d'),
        'next_week_date': next_week.strftime('%Y-%m-%d'),
        'hours': hours, # Liste des heures passée explicitement
    }
    
    return render(request, 'calendar.html', context)