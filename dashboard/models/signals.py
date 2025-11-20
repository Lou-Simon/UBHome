from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.utils import OperationalError
from datetime import timedelta, datetime, time 
from django.utils import timezone
from .models import Student, ForumChannel, Course, Email, ForumPost, Event 
import random # Ajout de l'import pour une potentielle future diversification des données

# --- DONNÉES ÉTUDIANTS (Gardées inchangées) ---
INITIAL_STUDENTS_DATA = [
            
            # --- L1 ISI ---
            {"student_id": "25001001", "email": "lucas.martin@hub.fr", "full_name": "Lucas Martin", "year": "L1 ISI", "password": "Kj8#mP2a"},
            {"student_id": "25001002", "email": "emma.bernard@hub.fr", "full_name": "Emma Bernard", "year": "L1 ISI", "password": "xR9!vL4z"},
            {"student_id": "25001003", "email": "hugo.dubois@hub.fr", "full_name": "Hugo Dubois", "year": "L1 ISI", "password": "T2p@qW8n"},
            {"student_id": "25001004", "email": "chloe.thomas@hub.fr", "full_name": "Chloé Thomas", "year": "L1 ISI", "password": "mB5$kS3d"},
            {"student_id": "25001005", "email": "nathan.robert@hub.fr", "full_name": "Nathan Robert", "year": "L1 ISI", "password": "G7y&fR9j"},

            # --- L2 IFA ---
            {"student_id": "24002001", "email": "lea.richard@hub.fr", "full_name": "Léa Richard", "year": "L2 IFA", "password": "H4n#dX2p"},
            {"student_id": "24002002", "email": "enzo.petit@hub.fr", "full_name": "Enzo Petit", "year": "L2 IFA", "password": "cL9@zM1w"},
            {"student_id": "24002003", "email": "manon.durand@hub.fr", "full_name": "Manon Durand", "year": "L2 IFA", "password": "V3k$rB8t"},
            {"student_id": "24002004", "email": "louis.leroy@hub.fr", "full_name": "Louis Leroy", "year": "L2 IFA", "password": "jS6!nF5q"},
            {"student_id": "24002005", "email": "jade.moreau@hub.fr", "full_name": "Jade Moreau", "year": "L2 IFA", "password": "P9m&gH2v"},

            # --- L3 IFA ---
            {"student_id": "23003001", "email": "gabriel.simon@hub.fr", "full_name": "Gabriel Simon", "year": "L3 IFA", "password": "X2z#kL7r"},
            {"student_id": "23003002", "email": "louise.laurent@hub.fr", "full_name": "Louise Laurent", "year": "L3 IFA", "password": "bN5@jT9y"},
            {"student_id": "23003003", "email": "adam.lefebvre@hub.fr", "full_name": "Adam Lefebvre", "year": "L3 IFA", "password": "R8v$mC4x"},
            {"student_id": "23003004", "email": "lina.michel@hub.fr", "full_name": "Lina Michel", "year": "L3 IFA", "password": "wQ3!pS6d"},
            {"student_id": "23003005", "email": "arthur.garcia@hub.fr", "full_name": "Arthur Garcia", "year": "L3 IFA", "password": "L7k&fH1n"},

            # --- M1 ILIADE ---
            {"student_id": "22204565", "email": "simon.dumas@hub.fr", "full_name": "Simon Dumas", "year": "M1 ILIADE", "password": "1234"},
            {"student_id": "22204198", "email": "lou.simon@hub.fr", "full_name": "Lou Simon", "year": "M1 ILIADE", "password": "1234"},
            {"student_id": "22101168", "email": "mael.bogaer@hub.fr", "full_name": "Maël Bogaër", "year": "M1 ILIADE", "password": "1234"},
            {"student_id": "22204202", "email": "zoe.vincent@hub.fr", "full_name": "Zoé Vincent", "year": "M1 ILIADE", "password": "dF3!hS9m"},
            {"student_id": "22204203", "email": "jules.fournier@hub.fr", "full_name": "Jules Fournier", "year": "M1 ILIADE", "password": "M8n&vL4q"},

            # --- M1 SIIA ---
            {"student_id": "22205001", "email": "mila.morel@hub.fr", "full_name": "Mila Morel", "year": "M1 SIIA", "password": "S2j#kR7t"},
            {"student_id": "22205002", "email": "mael.girard@hub.fr", "full_name": "Maël Girard", "year": "M1 SIIA", "password": "pG5@zV9x"},
            {"student_id": "22205003", "email": "elena.andre@hub.fr", "full_name": "Elena André", "year": "M1 SIIA", "password": "B8w$mC3n"},
            {"student_id": "22205004", "email": "noah.lefevre@hub.fr", "full_name": "Noah Lefèvre", "year": "M1 SIIA", "password": "hL4!nF8y"},
            {"student_id": "22205005", "email": "ambre.mercier@hub.fr", "full_name": "Ambre Mercier", "year": "M1 SIIA", "password": "Q9r&jT2k"},

            # --- M1 TILL-A ---
            {"student_id": "22206001", "email": "sacha.dupont@hub.fr", "full_name": "Sacha Dupont", "year": "M1 TILL-A", "password": "F3v#gP6m"},
            {"student_id": "22206002", "email": "mia.lambert@hub.fr", "full_name": "Mia Lambert", "year": "M1 TILL-A", "password": "zK7@dX1w"},
            {"student_id": "22206003", "email": "liam.bonnet@hub.fr", "full_name": "Liam Bonnet", "year": "M1 TILL-A", "password": "N4j$rS9t"},
            {"student_id": "22206004", "email": "rose.francois@hub.fr", "full_name": "Rose François", "year": "M1 TILL-A", "password": "cM8!hL2p"},
            {"student_id": "22206005", "email": "ethan.martinez@hub.fr", "full_name": "Ethan Martinez", "year": "M1 TILL-A", "password": "V5n&bC7q"},

            # --- M1 LSE ---
            {"student_id": "22207001", "email": "gabin.legah@hub.fr", "full_name": "Gabin Legah", "year": "M1 LSE", "password": "R9k#mF4z"},
            {"student_id": "22207002", "email": "anna.guerin@hub.fr", "full_name": "Anna Guérin", "year": "M1 LSE", "password": "wS2@jT6n"},
            {"student_id": "22207003", "email": "raphael.boyer@hub.fr", "full_name": "Raphaël Boyer", "year": "M1 LSE", "password": "L7v$gP3x"},
            {"student_id": "22207004", "email": "julia.fontaine@hub.fr", "full_name": "Julia Fontaine", "year": "M1 LSE", "password": "yH5!nC8m"},
            {"student_id": "22207005", "email": "tom.chevalier@hub.fr", "full_name": "Tom Chevalier", "year": "M1 LSE", "password": "K3r&bV1q"},

            # --- M2 ILIADE ---
            {"student_id": "21204101", "email": "lucie.blanc@hub.fr", "full_name": "Lucie Blanc", "year": "M2 ILIADE", "password": "M8j#dX5t"},
            {"student_id": "21204102", "email": "maxime.gauthier@hub.fr", "full_name": "Maxime Gauthier", "year": "M2 ILIADE", "password": "pL2@zS9w"},
            {"student_id": "21204103", "email": "camille.perrin@hub.fr", "full_name": "Camille Perrin", "year": "M2 ILIADE", "password": "F6v$mC4n"},
            {"student_id": "21204104", "email": "antoine.robin@hub.fr", "full_name": "Antoine Robin", "year": "M2 ILIADE", "password": "hT9!gR2k"},
            {"student_id": "21204105", "email": "victoire.clement@hub.fr", "full_name": "Victoire Clément", "year": "M2 ILIADE", "password": "B4n&jP7y"},

            # --- M2 SIIA ---
            {"student_id": "21205101", "email": "mathis.morin@hub.fr", "full_name": "Mathis Morin", "year": "M2 SIIA", "password": "Q7k#vL3m"},
            {"student_id": "21205102", "email": "elise.nicolas@hub.fr", "full_name": "Élise Nicolas", "year": "M2 SIIA", "password": "zS5@hF9x"},
            {"student_id": "21205103", "email": "evan.henry@hub.fr", "full_name": "Evan Henry", "year": "M2 SIIA", "password": "N2r$bC6p"},
            {"student_id": "21205104", "email": "margaux.rousse@hub.fr", "full_name": "Margaux Roussel", "year": "M2 SIIA", "password": "cV8!mJ1t"},
            {"student_id": "21205105", "email": "clement.mathieu@hub.fr", "full_name": "Clément Mathieu", "year": "M2 SIIA", "password": "L4n&gS7w"},

            # --- M2 TILL-A ---
            {"student_id": "21206101", "email": "clara.masson@hub.fr", "full_name": "Clara Masson", "year": "M2 TILL-A", "password": "H9v#kT2z"},
            {"student_id": "21206102", "email": "yanis.marchand@hub.fr", "full_name": "Yanis Marchand", "year": "M2 TILL-A", "password": "xP3@jR6n"},
            {"student_id": "21206103", "email": "sarah.duval@hub.fr", "full_name": "Sarah Duval", "year": "M2 TILL-A", "password": "M6k$bL9y"},
            {"student_id": "21206104", "email": "theo.denis@hub.fr", "full_name": "Théo Denis", "year": "M2 TILL-A", "password": "wJ2!fC5m"},
            {"student_id": "21206105", "email": "ines.dumont@hub.fr", "full_name": "Inès Dumont", "year": "M2 TILL-A", "password": "T8r&mS4q"},

            # --- M2 LSE ---
            {"student_id": "21207101", "email": "alexis.marie@hub.fr", "full_name": "Alexis Marie", "year": "M2 LSE", "password": "V4n#gH1k"},
            {"student_id": "21207102", "email": "lola.lemahieu@hub.fr", "full_name": "Lola Lemahieu", "year": "M2 LSE", "password": "pC9@zL5t"},
            {"student_id": "21207103", "email": "quentin.noel@hub.fr", "full_name": "Quentin Noël", "year": "M2 LSE", "password": "F2v$mS8x"},
            {"student_id": "21207104", "email": "oceane.meyer@hub.fr", "full_name": "Océane Meyer", "year": "M2 LSE", "password": "hR6!jT3w"},
            {"student_id": "21207105", "email": "robin.lucas@hub.fr", "full_name": "Robin Lucas", "year": "M2 LSE", "password": "S5k&bP9m"}
]

INITIAL_CHANNELS_DATA = [
    {"name": "General", "description": "Discussions générales sur la vie étudiante."},
    {"name": "L1 ISI", "description": "Discussions pour les étudiants L1 Informatique Scientifique et Ingénierie."},
    {"name": "L2 IFA", "description": "Discussions pour les étudiants L2 Informatique et Applications."},
    {"name": "L3 IFA", "description": "Discussions pour les étudiants L3 Informatique et Applications."},
    {"name": "M1 ILIADE", "description": "Master 1 Ingénierie du Logiciel et de l'Intelligence Artificielle pour les Données et l'Environnement."},
    {"name": "M1 SIIA", "description": "Master 1 Systèmes d'Information et Ingénierie d'Applications."},
    {"name": "M1 LSE", "description": "Master 1 Logistique et Systèmes d'Entreprise."},
    {"name": "M2 ILIADE", "description": "Master 2 Ingénierie du Logiciel et de l'Intelligence Artificielle pour les Données et l'Environnement."},
    {"name": "M2 SIIA", "description": "Master 2 Systèmes d'Information et Ingénierie d'Applications."},
    {"name": "M2 LSE", "description": "Master 2 Logistique et Systèmes d'Entreprise."},
]

# --- NOUVELLES DONNÉES DE COURS PLUS DIVERSES (Minimum 5 par filière) ---
INITIAL_COURSES_DATA = [
    # Cours L1
    {"name": "Introduction à l'Algorithmique", "teacher": "Mme. Duval"},
    {"name": "Base de Données SQL", "teacher": "M. Petit"},
    {"name": "Architecture des Ordinateurs", "teacher": "M. Leblanc"},
    {"name": "Mathématiques Discrètes", "teacher": "Mme. Dubois"},
    {"name": "Bureautique et Outils", "teacher": "M. Moreau"},
    
    # Cours L2/L3 IFA
    {"name": "Programmation Orientée Objet", "teacher": "Mme. Bernard"},
    {"name": "Réseaux et Sécurité", "teacher": "M. Martin"},
    {"name": "Programmation Fonctionnelle", "teacher": "M. Leroy"},
    {"name": "Système d'exploitation (OS)", "teacher": "M. Michel"},
    {"name": "Développement Web (Front-end)", "teacher": "M. Dupont"}, # L3
    {"name": "Conception BDD Avancée", "teacher": "M. Petit"}, # L3
    {"name": "Cryptographie", "teacher": "M. Martin"}, # L3
    {"name": "POO Avancée (Java/C#)", "teacher": "Mme. Bernard"}, # L3

    # Cours M1 ILIADE
    {"name": "Développement Web Avancé (Django)", "teacher": "M. Dupont"},
    {"name": "Intelligence Artificielle et ML", "teacher": "Mme. Lecoeur"},
    {"name": "Génie Logiciel (UML/Agile)", "teacher": "M. Simon"},
    {"name": "Cloud Computing", "teacher": "M. Guerin"},
    {"name": "Cybersécurité", "teacher": "M. Laurent"},
    
    # Cours M1 SIIA
    {"name": "Architecture d'Entreprise", "teacher": "M. Lefebvre"},
    {"name": "Ingénierie des Exigences", "teacher": "Mme. Marchand"},
    {"name": "Management de Projet", "teacher": "M. Dubois"},
    {"name": "Analyse Décisionnelle", "teacher": "Mme. Morin"},
    {"name": "Méthodes Agiles (Scrum)", "teacher": "M. Lambert"},
    
    # Cours M2 TILL-A
    {"name": "Recherche Opérationnelle", "teacher": "Mme. Martin"},
    {"name": "Projet de Fin d'Études", "teacher": "M. Richard"},
    {"name": "Modélisation Stochastique", "teacher": "M. Robert"},
    {"name": "Théorie de l'Information", "teacher": "Mme. Thomas"},
    {"name": "Optimisation Numérique", "teacher": "M. Dubois"},

    # Cours M2 ILIADE
    {"name": "Deep Learning", "teacher": "Mme. Lecoeur"},
    {"name": "Vision par Ordinateur", "teacher": "M. Simon"},
    {"name": "Développement Mobile", "teacher": "M. Dupont"},
    
    # Cours Transverses
    {"name": "Anglais Technique", "teacher": "Mme. Smith"},
    {"name": "Projet Annuel", "teacher": "Mme. Rossi"},
]

def generate_weekly_events(all_courses, start_date_aware):
    """Génère des événements récurrents pour plusieurs semaines avec une rotation hebdomadaire des jours."""
    
    # 0=Lundi, 1=Mardi, ..., 6=Dimanche
    SCHEDULE_DATA = [
        # L1 (5 cours)
        {"day_of_week": 0, "course_name": "Introduction à l'Algorithmique", "title": "CM Algo", "start_hour": 9, "end_hour": 12, "location": "Amphi A"},
        {"day_of_week": 1, "course_name": "Base de Données SQL", "title": "TD BDD SQL", "start_hour": 14, "end_hour": 17, "location": "Salle 101"},
        {"day_of_week": 2, "course_name": "Architecture des Ordinateurs", "title": "CM Architecture", "start_hour": 9, "end_hour": 12, "location": "Amphi B"},
        {"day_of_week": 3, "course_name": "Mathématiques Discrètes", "title": "TD Maths", "start_hour": 14, "end_hour": 16, "location": "Salle 205"},
        {"day_of_week": 4, "course_name": "Bureautique et Outils", "title": "TP Bureautique", "start_hour": 10, "end_hour": 12, "location": "Salle Info 1"},
        
        # L2 IFA (5 cours)
        {"day_of_week": 0, "course_name": "Programmation Orientée Objet", "title": "CM POO", "start_hour": 14, "end_hour": 17, "location": "Amphi C"},
        {"day_of_week": 1, "course_name": "Réseaux et Sécurité", "title": "TD Réseaux", "start_hour": 9, "end_hour": 12, "location": "Salle 202"},
        {"day_of_week": 2, "course_name": "Programmation Fonctionnelle", "title": "CM Fonctionnelle", "start_hour": 14, "end_hour": 16, "location": "Salle 203"},
        {"day_of_week": 3, "course_name": "Système d'exploitation (OS)", "title": "TD OS", "start_hour": 9, "end_hour": 12, "location": "Amphi D"},
        {"day_of_week": 4, "course_name": "Anglais Technique", "title": "Anglais L2", "start_hour": 14, "end_hour": 16, "location": "Salle 301"},
        
        # L3 IFA (5 cours)
        {"day_of_week": 0, "course_name": "Développement Web (Front-end)", "title": "CM Web Front", "start_hour": 9, "end_hour": 12, "location": "Amphi D"},
        {"day_of_week": 1, "course_name": "Conception BDD Avancée", "title": "TD BDD Avancée", "start_hour": 14, "end_hour": 17, "location": "Salle 302"},
        {"day_of_week": 2, "course_name": "Cryptographie", "title": "CM Crypto", "start_hour": 9, "end_hour": 11, "location": "Salle 303"},
        {"day_of_week": 3, "course_name": "POO Avancée (Java/C#)", "title": "TP POO Avancée", "start_hour": 14, "end_hour": 17, "location": "Salle Info 6"},
        {"day_of_week": 4, "course_name": "Génie Logiciel (UML/Agile)", "title": "CM Génie Logiciel", "start_hour": 9, "end_hour": 12, "location": "Amphi A"},

        # M1 ILIADE (5 cours) - Le profil de Simon Dumas
        {"day_of_week": 0, "course_name": "Développement Web Avancé (Django)", "title": "CM Dev Web Avancé", "start_hour": 9, "end_hour": 12, "location": "Amphi A"},
        {"day_of_week": 1, "course_name": "Intelligence Artificielle et ML", "title": "TD IA & ML", "start_hour": 9, "end_hour": 12, "location": "Salle 402"},
        {"day_of_week": 2, "course_name": "Génie Logiciel (UML/Agile)", "title": "CM Génie Logiciel", "start_hour": 14, "end_hour": 17, "location": "Salle 403"},
        {"day_of_week": 3, "course_name": "Cloud Computing", "title": "CM Cloud", "start_hour": 9, "end_hour": 12, "location": "Amphi B"},
        {"day_of_week": 4, "course_name": "Cybersécurité", "title": "TD Cyber", "start_hour": 14, "end_hour": 16, "location": "Salle 405"},
        
        # M1 SIIA (5 cours)
        {"day_of_week": 0, "course_name": "Architecture d'Entreprise", "title": "CM Archi Ent.", "start_hour": 14, "end_hour": 17, "location": "Amphi E"},
        {"day_of_week": 1, "course_name": "Ingénierie des Exigences", "title": "TD Exigences", "start_hour": 9, "end_hour": 12, "location": "Salle 501"},
        {"day_of_week": 2, "course_name": "Management de Projet", "title": "CM Management", "start_hour": 9, "end_hour": 12, "location": "Amphi C"},
        {"day_of_week": 3, "course_name": "Analyse Décisionnelle", "title": "TD Décisionnel", "start_hour": 14, "end_hour": 17, "location": "Salle 502"},
        {"day_of_week": 4, "course_name": "Méthodes Agiles (Scrum)", "title": "TP Scrum", "start_hour": 9, "end_hour": 12, "location": "Salle Info 7"},
        
        # M2 TILL-A (5 cours)
        {"day_of_week": 0, "course_name": "Recherche Opérationnelle", "title": "CM RO", "start_hour": 9, "end_hour": 12, "location": "Amphi F"},
        {"day_of_week": 1, "course_name": "Modélisation Stochastique", "title": "CM Stochastique", "start_hour": 14, "end_hour": 17, "location": "Salle 601"},
        {"day_of_week": 2, "course_name": "Théorie de l'Information", "title": "TD Info", "start_hour": 9, "end_hour": 12, "location": "Amphi E"},
        {"day_of_week": 3, "course_name": "Optimisation Numérique", "title": "CM Optimisation", "start_hour": 14, "end_hour": 17, "location": "Salle 602"},
        {"day_of_week": 4, "course_name": "Projet de Fin d'Études", "title": "Suivi PFE", "start_hour": 9, "end_hour": 11, "location": "Bureau R1"},
        
        # Événement unique: Examen (L1 Algo)
        # On ne crée l'événement unique que pour la première semaine
        {"day_of_week": 2, "course_name": "Introduction à l'Algorithmique", "title": "Examen - Intro Algo", "start_hour": 14, "end_hour": 17, "location": "Salle 103", "is_single": True},
    ]
    
    events_to_create = []
    
    # Obtenir la date du Lundi de la semaine en cours
    date_lundi = start_date_aware.date() + timedelta(days=-start_date_aware.weekday())
    
    # Générer 6 semaines de données hebdomadaires (couvre largement jusqu'à début Décembre)
    target_date = date_lundi + timedelta(weeks=6)

    current_date = date_lundi
    week_count = 0 # Compteur pour alterner les emplois du temps
    
    while current_date < target_date:
        
        # Décalage de jour : 0 (Semaine 0, 2, 4...) ou 1 (Semaine 1, 3, 5...)
        # Cela crée une rotation de 1 jour sur les semaines impaires
        day_shift = week_count % 2 
        
        # Pour chaque semaine, on parcourt l'emploi du temps
        for schedule in SCHEDULE_DATA:
            
            # Gestion de l'examen: NE JAMAIS LE DÉCALER et NE LE CRÉER QUE LA PREMIÈRE SEMAINE
            if schedule.get("is_single"):
                if current_date != date_lundi: 
                    continue 
                # L'examen se passe au jour initial (pas de shift)
                final_day_of_week = schedule["day_of_week"]
            else:
                # Appliquer le décalage cyclique (0=Lundi à 4=Vendredi)
                initial_day = schedule["day_of_week"]
                final_day_of_week = (initial_day + day_shift) % 5 
                
                # On ne veut pas d'événements le week-end (5 et 6). 
                # Si le jour initial était 4 (Vendredi) et le shift est de 1, 
                # il passe à 0 (Lundi). Ceci est géré par le % 5.

            # Calculer la date de l'événement dans la semaine
            event_day_date = current_date + timedelta(days=final_day_of_week)
            
            try:
                course = all_courses.get(name=schedule["course_name"])
                
                # Créer le datetime aware pour le début et la fin
                start_time_local = timezone.make_aware(datetime.combine(event_day_date, time(schedule["start_hour"], 0)))
                end_time_local = timezone.make_aware(datetime.combine(event_day_date, time(schedule["end_hour"], 0)))
                
                events_to_create.append(Event(
                    course=course,
                    title=schedule["title"],
                    location=schedule["location"],
                    start_time=start_time_local,
                    end_time=end_time_local
                ))
            except Course.DoesNotExist:
                print(f"ATTENTION: Cours non trouvé pour l'événement : {schedule['course_name']}")
                pass
        
        # Passer à la semaine suivante
        current_date += timedelta(weeks=1)
        week_count += 1

    Event.objects.bulk_create(events_to_create)
    print(f"✅ {len(events_to_create)} événements hebdomadaires créés avec rotation jusqu'à {target_date.strftime('%d/%m')}.")


def create_initial_content(all_students, all_channels, all_courses):
    """Crée l'inscription aux cours, l'email, le post et les événements initiaux."""
    
    # --- 1. Logique d'inscription des étudiants (Mise à jour pour 5+ cours) ---
    for student in all_students:
        try:
            # Récupère le nom complet du cours pour la filière
            if 'L1' in student.year:
                courses_to_enroll = [
                    "Introduction à l'Algorithmique", 
                    "Base de Données SQL", 
                    "Architecture des Ordinateurs", 
                    "Mathématiques Discrètes",
                    "Bureautique et Outils"
                ]
            elif 'L2 IFA' in student.year:
                courses_to_enroll = [
                    "Programmation Orientée Objet", 
                    "Réseaux et Sécurité",
                    "Programmation Fonctionnelle",
                    "Système d'exploitation (OS)",
                    "Anglais Technique"
                ]
            elif 'L3 IFA' in student.year:
                courses_to_enroll = [
                    "Développement Web (Front-end)",
                    "Conception BDD Avancée",
                    "Cryptographie",
                    "POO Avancée (Java/C#)",
                    "Génie Logiciel (UML/Agile)"
                ]
            elif 'M1 ILIADE' in student.year:
                courses_to_enroll = [
                    "Développement Web Avancé (Django)", 
                    "Intelligence Artificielle et ML", 
                    "Génie Logiciel (UML/Agile)",
                    "Cloud Computing",
                    "Cybersécurité"
                ]
            elif 'M1 SIIA' in student.year:
                courses_to_enroll = [
                    "Architecture d'Entreprise",
                    "Ingénierie des Exigences",
                    "Management de Projet",
                    "Analyse Décisionnelle",
                    "Méthodes Agiles (Scrum)"
                ]
            elif 'M2 TILL-A' in student.year:
                courses_to_enroll = [
                    "Recherche Opérationnelle", 
                    "Projet de Fin d'Études", 
                    "Modélisation Stochastique",
                    "Théorie de l'Information",
                    "Optimisation Numérique"
                ]
            elif 'M2 ILIADE' in student.year:
                 courses_to_enroll = [
                    "Deep Learning",
                    "Vision par Ordinateur",
                    "Développement Mobile",
                    "Génie Logiciel (UML/Agile)",
                    "Cloud Computing"
                ]
            else:
                courses_to_enroll = ["Anglais Technique"] # Minimum
            
            # Inscrit l'étudiant aux cours
            course_objects = [all_courses.get(name=name) for name in courses_to_enroll if all_courses.filter(name=name).exists()]
            if course_objects:
                student.courses.add(*course_objects)

        except Course.DoesNotExist: 
            pass
        
    
    # --- 2. Contenu initial (Email, Post) ---

    # Email : Simon (M1 ILIADE) envoie à Lou (M1 ILIADE)
    try:
        sender = all_students.get(full_name="Simon Dumas")
        recipient = all_students.get(full_name="Lou Simon")
        Email.objects.create(
            sender=sender,
            recipient=recipient,
            subject="Bienvenue sur la nouvelle messagerie",
            body="Bonjour Lou, content de voir que la messagerie fonctionne après la refactorisation ! À bientôt."
        )
    except Student.DoesNotExist:
        pass 
    
    # Forum Post : Maël (M1 ILIADE) post dans le canal M1 ILIADE
    try:
        author = all_students.get(full_name="Maël Bogaër")
        channel = all_channels.get(name="M1 ILIADE")
        ForumPost.objects.create(
            channel=channel,
            author=author,
            content="Bonjour à tous les M1 ILIADE ! N'hésitez pas à poster vos questions sur les TP ici. Bon courage pour les premiers modules !"
        )
    except (Student.DoesNotExist, ForumChannel.DoesNotExist):
        pass

    # --- 3. Ajout d'événements (Calendrier) ---
    
    # 1. Obtenir le datetime aware actuel
    start_date_aware = timezone.now()
    
    # 2. Générer les événements récurrents
    try:
        generate_weekly_events(all_courses, start_date_aware)
        
    except Course.DoesNotExist: 
        pass


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    """Crée les comptes, canaux, cours et contenu initiaux après les migrations."""
    
    if sender.name != 'dashboard':
        return

    try:
        # 1. Insertion des Étudiants (Si la table est vide)
        if not Student.objects.exists():
            for data in INITIAL_STUDENTS_DATA:
                Student.objects.create(**data)
            print("✅ Données initiales des étudiants insérées.")
        
        # Récupération des étudiants pour les FK
        all_students = Student.objects.all() 
        
        # 2. Insertion des Canaux de Forum
        if not ForumChannel.objects.exists():
            for data in INITIAL_CHANNELS_DATA:
                ForumChannel.objects.create(**data)
            print("✅ Canaux de forum initiaux insérés.")
            
        # Récupération des canaux pour les FK
        all_channels = ForumChannel.objects.all()

        # 3. Insertion des Cours (MIS À JOUR)
        if Course.objects.count() != len(INITIAL_COURSES_DATA):
            # Suppression et recréation si le nombre ne correspond pas à la nouvelle liste
            Course.objects.all().delete()
            for data in INITIAL_COURSES_DATA:
                Course.objects.create(**data)
            print("✅ Cours initiaux (mis à jour) insérés.")
            
        # Récupération des cours pour les FK
        all_courses = Course.objects.all()

        # 4. Insertion du Contenu Initial et Inscriptions
        # Si la base est prête (Étudiants, Canaux, Cours existent), mais pas les Emails (le contenu initial)
        if all_students.exists() and all_channels.exists() and all_courses.exists() and not Email.objects.exists():
             create_initial_content(all_students, all_channels, all_courses)
             print("✅ Contenu initial (Email, Post, Events et Inscriptions) inséré.")
             
    except OperationalError as e:
        # Gère le cas où la BDD n'est pas encore complètement créée 
        pass