# Fichier : dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone 
from datetime import timedelta, datetime
from django.db.models import Q 
from ..models import Student, Event, Email  # AJOUT : Import du modèle Email
from .auth import get_session_user_data 
import logging

logger = logging.getLogger(__name__)

# --- FONCTION UTILITAIRE POUR ENVOYER DES NOTIFICATIONS ---
def send_event_notification(sender_student, recipient_student, event, event_date_str):
    """
    Crée et envoie un email de notification pour informer un participant 
    qu'il a été ajouté à un événement.
    """
    subject = f"Nouvel événement : {event.title}"
    
    body = f"""Bonjour {recipient_student.full_name},

Vous avez été ajouté(e) à un nouvel événement par {sender_student.full_name}.

📅 Détails de l'événement :
- Titre : {event.title}
- Date : {event_date_str}
- Heure de début : {timezone.localtime(event.start_time).strftime('%H:%M')}
- Heure de fin : {timezone.localtime(event.end_time).strftime('%H:%M')}
- Lieu : {event.location if event.location else 'Non spécifié'}

Cordialement,
Le système de gestion des événements"""
    
    try:
        Email.objects.create(
            sender=sender_student,
            recipient=recipient_student,
            subject=subject,
            body=body,
            is_draft=False
        )
        logger.info(f"Email de notification envoyé à {recipient_student.full_name} pour l'événement {event.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la notification email : {e}")


# --- VUE POUR LA SUPPRESSION ---
@require_http_methods(["POST"])
def delete_event(request, event_id):
    """
    Gère la suppression des événements personnels.
    Redirige avec un message d'erreur si l'événement est un cours ou si l'utilisateur n'est pas un participant.
    """
    user_data = get_session_user_data(request)
    if not user_data:
        return redirect('dashboard:login')

    event = get_object_or_404(Event, id=event_id)
    
    # Trouver le chemin de base pour la redirection (e.g., '/calendar/')
    try:
        base_path = '/'.join(request.path_info.split('/delete/')[:-1]) + '/'
    except IndexError:
        base_path = '/calendar/'

    # 1. Vérification : Est-ce un événement de cours ? Si oui, refuser la suppression.
    if event.course is not None:
        redirect_date = timezone.localtime(event.start_time).strftime('%Y-%m-%d')
        return redirect(f"{base_path}?error=notcourse&date={redirect_date}")

    # 2. Vérification : L'utilisateur actuel participe-t-il à cet événement personnel ?
    try:
        current_student = Student.objects.get(student_id=user_data['student_id'])
    except Student.DoesNotExist:
        return redirect('dashboard:login')

    if current_student not in event.attendees.all():
        redirect_date = timezone.localtime(event.start_time).strftime('%Y-%m-%d')
        return redirect(f"{base_path}?error=unauthorized&date={redirect_date}")

    # 3. Suppression
    try:
        redirect_date = timezone.localtime(event.start_time).strftime('%Y-%m-%d')
        event.delete()
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'événement {event_id}: {e}")
        return redirect(f"{base_path}?error=delete_failed&date={redirect_date}")
    
    # Succès
    return redirect(f"{base_path}?success=deleted&date={redirect_date}")


def calendar(request):
    """
    Vue pour afficher la page du calendrier, y compris la navigation hebdomadaire, 
    le filtrage des événements de l'étudiant, la création (POST) et l'affichage des messages.
    """
    
    user_data = get_session_user_data(request)
    if not user_data:
        return redirect('dashboard:login')
    
    try:
        current_student = Student.objects.get(student_id=user_data['student_id'])
    except Student.DoesNotExist:
        return redirect('dashboard:login') 
    
    enrolled_course_ids = current_student.courses.values_list('id', flat=True)

    form_error_message = None
    form_data = {}

    # --- GESTION DE LA CRÉATION D'ÉVÉNEMENT (POST) ---
    if request.method == 'POST':
        # Sauvegarde des données POST pour les réafficher en cas d'erreur
        form_data = request.POST

        try:
            # Récupérer les données du formulaire
            title = request.POST.get('title')
            location = request.POST.get('location')
            date_str = request.POST.get('date')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            attendee_ids = request.POST.getlist('attendees')
            
            # Reconstitution de l'objet datetime
            start_datetime = timezone.make_aware(datetime.strptime(f"{date_str} {start_time_str}", '%Y-%m-%d %H:%M'))
            end_datetime = timezone.make_aware(datetime.strptime(f"{date_str} {end_time_str}", '%Y-%m-%d %H:%M'))

            # 1. Validation de l'ordre des heures
            if start_datetime >= end_datetime:
                form_error_message = "L'heure de début doit être strictement antérieure à l'heure de fin."
                raise ValueError("Heure invalide.")

            # 2. Validation de la date antérieure
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date() 
            
            if event_date < timezone.localdate(): 
                form_error_message = "La date de l'événement ne peut pas être antérieure à la date du jour."
                raise ValueError("Date antérieure interdite.")

            # 3. Vérification de Conflit
            events_to_check_filter = (
                Q(course_id__in=enrolled_course_ids) |
                Q(attendees=current_student)
            )

            overlapping_events_exist = Event.objects.filter(
                events_to_check_filter,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime
            ).exists()

            if overlapping_events_exist:
                form_error_message = "Conflit : Cet événement chevauche un cours ou un autre événement personnel déjà planifié. Veuillez ajuster les heures."
                raise ValueError("Conflit d'horaire.")
            
            # --- CRÉATION DE L'ÉVÉNEMENT (si PAS de conflit) ---
            new_event = Event.objects.create(
                title=title,
                location=location,
                start_time=start_datetime,
                end_time=end_datetime,
                course=None 
            )
            
            # Ajout de l'étudiant courant
            new_event.attendees.add(current_student)
            
            # NOUVEAU : Formatage de la date pour les emails
            event_date_formatted = event_date.strftime('%d/%m/%Y')
            
            # NOUVEAU : Ajout des autres participants + envoi d'email de notification
            for student_id in attendee_ids:
                try:
                    attendee = Student.objects.get(student_id=student_id)
                    new_event.attendees.add(attendee)
                    
                    # Envoyer un email de notification au participant
                    send_event_notification(
                        sender_student=current_student,
                        recipient_student=attendee,
                        event=new_event,
                        event_date_str=event_date_formatted
                    )
                except Student.DoesNotExist:
                    logger.warning(f"Étudiant avec ID {student_id} introuvable")
                    pass 

            # Succès : redirection
            return redirect(f"{request.path_info}?success=created&date={date_str}")

        except ValueError:
            # form_error_message est déjà défini
            pass 
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'événement : {e}")
            form_error_message = f"Une erreur inattendue est survenue lors de la création."


    # --- 2. Détermination de la semaine courante (GET) ---
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            current_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.localdate()
    else:
        current_date = timezone.localdate() 
    
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_displayed_week = start_of_week + timedelta(days=4)
    end_of_query_week = start_of_week + timedelta(days=6)

    # --- 3. Récupération et organisation des événements ---
    
    events_filter = (
        Q(course_id__in=enrolled_course_ids) |
        Q(attendees=current_student)
    )

    all_events = Event.objects.select_related('course').prefetch_related('attendees').filter(
        events_filter,
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_query_week
    ).order_by('start_time').distinct()
    
    events_by_day = {}
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'] 
    
    for i in range(5): 
        date = start_of_week + timedelta(days=i)
        events_by_day[i] = {
            'day_name': day_names[i],
            'date': date,
            'events': []
        }
    
    PX_PER_HOUR = 100
    START_HOUR_CALENDAR = 8

    for event in all_events:
        local_start_time = timezone.localtime(event.start_time)
        local_end_time = timezone.localtime(event.end_time)

        day_index = (local_start_time.date() - start_of_week).days
        
        if 0 <= day_index < 5:
            start_hour = local_start_time.hour
            start_minute = local_start_time.minute
            hour_offset = (start_hour - START_HOUR_CALENDAR) * PX_PER_HOUR
            minute_offset = int((start_minute / 60) * PX_PER_HOUR)
            event.total_start_offset = max(0, hour_offset + minute_offset)
            
            duration = (local_end_time - local_start_time).total_seconds() / 3600
            event.height = int(duration * PX_PER_HOUR)
            
            if event.course is None:
                color_code = 'primary'
                display_name = event.title
                event.is_personal_event = True 
            else:
                color_map = {0: 'teal', 1: 'indigo', 2: 'primary', 3: 'red'}
                color_key = event.course.id % 4 
                color_code = color_map.get(color_key, 'primary')
                display_name = event.course.name
                event.is_personal_event = False 
            
            event.color_code = color_code
            event.display_name = display_name 
            event.local_start_time = local_start_time
            event.local_end_time = local_end_time
            event.location = event.location if event.location else 'Non spécifié'
            
            events_by_day[day_index]['events'].append(event)


    # --- 4. Contexte pour le Template ---
    
    prev_week = start_of_week - timedelta(weeks=1)
    next_week = start_of_week + timedelta(weeks=1)
    
    week_days_list = [events_by_day[i] for i in range(5)] 
    
    current_week_label = f"Semaine du {start_of_week.strftime('%d %B')} au {end_of_displayed_week.strftime('%d %B %Y')}"
    
    hours = range(8, 18)
    
    all_other_students = Student.objects.exclude(student_id=current_student.student_id).order_by('full_name')
    
    should_open_modal = form_error_message is not None or request.GET.get('error') == 'form_post'

    # Gestion des messages d'erreur de suppression
    delete_error_message = None
    error_type = request.GET.get('error')

    if error_type == 'notcourse':
        delete_error_message = "❌ Erreur : Vous ne pouvez pas supprimer un événement de type 'Cours'. Seuls les événements personnels peuvent être supprimés."
    elif error_type == 'unauthorized':
        delete_error_message = "🔒 Erreur : Vous n'êtes pas autorisé à supprimer cet événement personnel car vous n'y participez pas."
    elif error_type == 'delete_failed':
        delete_error_message = "🛑 Erreur : La suppression de l'événement a échoué en raison d'un problème serveur."


    context = {
        'user': user_data,
        'title': 'Calendrier',
        'current_date': current_date.strftime('%Y-%m-%d'), 
        'week_days': week_days_list, 
        'current_week_label': current_week_label,
        'prev_week_date': prev_week.strftime('%Y-%m-%d'),
        'next_week_date': next_week.strftime('%Y-%m-%d'),
        'hours': hours,
        'all_other_students': all_other_students,
        
        # MESSAGES ET FORMULAIRE
        'form_error_message': form_error_message,
        'form_data': form_data,
        'should_open_modal': str(should_open_modal),
        'success_message': request.GET.get('success') == 'created', 
        'delete_success': request.GET.get('success') == 'deleted', 
        'delete_error_message': delete_error_message, 
    }
    
    return render(request, 'calendar.html', context)