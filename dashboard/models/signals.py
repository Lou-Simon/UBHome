
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.utils import OperationalError
# Importe tous les modèles
from .models import Student, ForumChannel, Course, Email, ForumPost, Event 
# Pas besoin d'importer le modèle séparément si tout est dans models.py

# Contient toutes vos données initiales (assurez-vous d'inclure la liste complète)
INITIAL_STUDENTS_DATA = [
            
            # --- L1 ISI ---
            {"student_id": "25001001", "email": "lucas.martin@hub.fr", "full_name": "Lucas Martin", "year": "L1 ISI", "password_clear": "Kj8#mP2a"},
            {"student_id": "25001002", "email": "emma.bernard@hub.fr", "full_name": "Emma Bernard", "year": "L1 ISI", "password_clear": "xR9!vL4z"},
            {"student_id": "25001003", "email": "hugo.dubois@hub.fr", "full_name": "Hugo Dubois", "year": "L1 ISI", "password_clear": "T2p@qW8n"},
            {"student_id": "25001004", "email": "chloe.thomas@hub.fr", "full_name": "Chloé Thomas", "year": "L1 ISI", "password_clear": "mB5$kS3d"},
            {"student_id": "25001005", "email": "nathan.robert@hub.fr", "full_name": "Nathan Robert", "year": "L1 ISI", "password_clear": "G7y&fR9j"},

            # --- L2 IFA ---
            {"student_id": "24002001", "email": "lea.richard@hub.fr", "full_name": "Léa Richard", "year": "L2 IFA", "password_clear": "H4n#dX2p"},
            {"student_id": "24002002", "email": "enzo.petit@hub.fr", "full_name": "Enzo Petit", "year": "L2 IFA", "password_clear": "cL9@zM1w"},
            {"student_id": "24002003", "email": "manon.durand@hub.fr", "full_name": "Manon Durand", "year": "L2 IFA", "password_clear": "V3k$rB8t"},
            {"student_id": "24002004", "email": "louis.leroy@hub.fr", "full_name": "Louis Leroy", "year": "L2 IFA", "password_clear": "jS6!nF5q"},
            {"student_id": "24002005", "email": "jade.moreau@hub.fr", "full_name": "Jade Moreau", "year": "L2 IFA", "password_clear": "P9m&gH2v"},

            # --- L3 IFA ---
            {"student_id": "23003001", "email": "gabriel.simon@hub.fr", "full_name": "Gabriel Simon", "year": "L3 IFA", "password_clear": "X2z#kL7r"},
            {"student_id": "23003002", "email": "louise.laurent@hub.fr", "full_name": "Louise Laurent", "year": "L3 IFA", "password_clear": "bN5@jT9y"},
            {"student_id": "23003003", "email": "adam.lefebvre@hub.fr", "full_name": "Adam Lefebvre", "year": "L3 IFA", "password_clear": "R8v$mC4x"},
            {"student_id": "23003004", "email": "lina.michel@hub.fr", "full_name": "Lina Michel", "year": "L3 IFA", "password_clear": "wQ3!pS6d"},
            {"student_id": "23003005", "email": "arthur.garcia@hub.fr", "full_name": "Arthur Garcia", "year": "L3 IFA", "password_clear": "L7k&fH1n"},

            # --- M1 ILIADE ---
            {"student_id": "22204565", "email": "simon.dumas@hub.fr", "full_name": "Simon Dumas", "year": "M1 ILIADE", "password_clear": "1234"},
            {"student_id": "22204198", "email": "lou.simon@hub.fr", "full_name": "Lou Simon", "year": "M1 ILIADE", "password_clear": "1234"},
            {"student_id": "22101168", "email": "mael.bogaer@hub.fr", "full_name": "Maël Bogaër", "year": "M1 ILIADE", "password_clear": "1234"},
            {"student_id": "22204202", "email": "zoe.vincent@hub.fr", "full_name": "Zoé Vincent", "year": "M1 ILIADE", "password_clear": "dF3!hS9m"},
            {"student_id": "22204203", "email": "jules.fournier@hub.fr", "full_name": "Jules Fournier", "year": "M1 ILIADE", "password_clear": "M8n&vL4q"},

            # --- M1 SIIA ---
            {"student_id": "22205001", "email": "mila.morel@hub.fr", "full_name": "Mila Morel", "year": "M1 SIIA", "password_clear": "S2j#kR7t"},
            {"student_id": "22205002", "email": "mael.girard@hub.fr", "full_name": "Maël Girard", "year": "M1 SIIA", "password_clear": "pG5@zV9x"},
            {"student_id": "22205003", "email": "elena.andre@hub.fr", "full_name": "Elena André", "year": "M1 SIIA", "password_clear": "B8w$mC3n"},
            {"student_id": "22205004", "email": "noah.lefevre@hub.fr", "full_name": "Noah Lefèvre", "year": "M1 SIIA", "password_clear": "hL4!nF8y"},
            {"student_id": "22205005", "email": "ambre.mercier@hub.fr", "full_name": "Ambre Mercier", "year": "M1 SIIA", "password_clear": "Q9r&jT2k"},

            # --- M1 TILL-A ---
            {"student_id": "22206001", "email": "sacha.dupont@hub.fr", "full_name": "Sacha Dupont", "year": "M1 TILL-A", "password_clear": "F3v#gP6m"},
            {"student_id": "22206002", "email": "mia.lambert@hub.fr", "full_name": "Mia Lambert", "year": "M1 TILL-A", "password_clear": "zK7@dX1w"},
            {"student_id": "22206003", "email": "liam.bonnet@hub.fr", "full_name": "Liam Bonnet", "year": "M1 TILL-A", "password_clear": "N4j$rS9t"},
            {"student_id": "22206004", "email": "rose.francois@hub.fr", "full_name": "Rose François", "year": "M1 TILL-A", "password_clear": "cM8!hL2p"},
            {"student_id": "22206005", "email": "ethan.martinez@hub.fr", "full_name": "Ethan Martinez", "year": "M1 TILL-A", "password_clear": "V5n&bC7q"},

            # --- M1 LSE ---
            {"student_id": "22207001", "email": "gabin.legah@hub.fr", "full_name": "Gabin Legah", "year": "M1 LSE", "password_clear": "R9k#mF4z"},
            {"student_id": "22207002", "email": "anna.guerin@hub.fr", "full_name": "Anna Guérin", "year": "M1 LSE", "password_clear": "wS2@jT6n"},
            {"student_id": "22207003", "email": "raphael.boyer@hub.fr", "full_name": "Raphaël Boyer", "year": "M1 LSE", "password_clear": "L7v$gP3x"},
            {"student_id": "22207004", "email": "julia.fontaine@hub.fr", "full_name": "Julia Fontaine", "year": "M1 LSE", "password_clear": "yH5!nC8m"},
            {"student_id": "22207005", "email": "tom.chevalier@hub.fr", "full_name": "Tom Chevalier", "year": "M1 LSE", "password_clear": "K3r&bV1q"},

            # --- M2 ILIADE ---
            {"student_id": "21204101", "email": "lucie.blanc@hub.fr", "full_name": "Lucie Blanc", "year": "M2 ILIADE", "password_clear": "M8j#dX5t"},
            {"student_id": "21204102", "email": "maxime.gauthier@hub.fr", "full_name": "Maxime Gauthier", "year": "M2 ILIADE", "password_clear": "pL2@zS9w"},
            {"student_id": "21204103", "email": "camille.perrin@hub.fr", "full_name": "Camille Perrin", "year": "M2 ILIADE", "password_clear": "F6v$mC4n"},
            {"student_id": "21204104", "email": "antoine.robin@hub.fr", "full_name": "Antoine Robin", "year": "M2 ILIADE", "password_clear": "hT9!gR2k"},
            {"student_id": "21204105", "email": "victoire.clement@hub.fr", "full_name": "Victoire Clément", "year": "M2 ILIADE", "password_clear": "B4n&jP7y"},

            # --- M2 SIIA ---
            {"student_id": "21205101", "email": "mathis.morin@hub.fr", "full_name": "Mathis Morin", "year": "M2 SIIA", "password_clear": "Q7k#vL3m"},
            {"student_id": "21205102", "email": "elise.nicolas@hub.fr", "full_name": "Élise Nicolas", "year": "M2 SIIA", "password_clear": "zS5@hF9x"},
            {"student_id": "21205103", "email": "evan.henry@hub.fr", "full_name": "Evan Henry", "year": "M2 SIIA", "password_clear": "N2r$bC6p"},
            {"student_id": "21205104", "email": "margaux.rousse@hub.fr", "full_name": "Margaux Roussel", "year": "M2 SIIA", "password_clear": "cV8!mJ1t"},
            {"student_id": "21205105", "email": "clement.mathieu@hub.fr", "full_name": "Clément Mathieu", "year": "M2 SIIA", "password_clear": "L4n&gS7w"},

            # --- M2 TILL-A ---
            {"student_id": "21206101", "email": "clara.masson@hub.fr", "full_name": "Clara Masson", "year": "M2 TILL-A", "password_clear": "H9v#kT2z"},
            {"student_id": "21206102", "email": "yanis.marchand@hub.fr", "full_name": "Yanis Marchand", "year": "M2 TILL-A", "password_clear": "xP3@jR6n"},
            {"student_id": "21206103", "email": "sarah.duval@hub.fr", "full_name": "Sarah Duval", "year": "M2 TILL-A", "password_clear": "M6k$bL9y"},
            {"student_id": "21206104", "email": "theo.denis@hub.fr", "full_name": "Théo Denis", "year": "M2 TILL-A", "password_clear": "wJ2!fC5m"},
            {"student_id": "21206105", "email": "ines.dumont@hub.fr", "full_name": "Inès Dumont", "year": "M2 TILL-A", "password_clear": "T8r&mS4q"},

            # --- M2 LSE ---
            {"student_id": "21207101", "email": "alexis.marie@hub.fr", "full_name": "Alexis Marie", "year": "M2 LSE", "password_clear": "V4n#gH1k"},
            {"student_id": "21207102", "email": "lola.lemahieu@hub.fr", "full_name": "Lola Lemahieu", "year": "M2 LSE", "password_clear": "pC9@zL5t"},
            {"student_id": "21207103", "email": "quentin.noel@hub.fr", "full_name": "Quentin Noël", "year": "M2 LSE", "password_clear": "F2v$mS8x"},
            {"student_id": "21207104", "email": "oceane.meyer@hub.fr", "full_name": "Océane Meyer", "year": "M2 LSE", "password_clear": "hR6!jT3w"},
            {"student_id": "21207105", "email": "robin.lucas@hub.fr", "full_name": "Robin Lucas", "year": "M2 LSE", "password_clear": "S5k&bP9m"}
]

# --- NOUVELLES DONNÉES INITIALES ---

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

INITIAL_COURSES_DATA = [
    {"name": "Développement Web Avancé", "teacher": "M. Dupont"},
    {"name": "Intelligence Artificielle", "teacher": "Mme. Lecoeur"},
    {"name": "Base de Données SQL", "teacher": "M. Petit"},
    {"name": "Anglais Technique", "teacher": "Mme. Smith"},
]

# --- AJOUT DE L'EMAIL ET DU POST INITIAL ---

def create_initial_content(students, channels, courses):
    """Crée un email, un post et un événement initial pour peupler la BDD."""
    
    # Email : Simon (M1 ILIADE) envoie à Lou (M1 ILIADE)
    try:
        sender = students.get(full_name="Simon Dumas")
        recipient = students.get(full_name="Lou Simon")
        Email.objects.create(
            sender=sender,
            recipient=recipient,
            subject="Bienvenue sur la nouvelle messagerie",
            body="Bonjour Lou, content de voir que la messagerie fonctionne après la refactorisation ! À bientôt."
        )
    except Student.DoesNotExist:
        pass # Ignorer si les étudiants initiaux ne sont pas là
    
    # Forum Post : Maël (M1 ILIADE) post dans le canal M1 ILIADE
    try:
        author = students.get(full_name="Maël Bogaër")
        channel = channels.get(name="M1 ILIADE")
        ForumPost.objects.create(
            channel=channel,
            author=author,
            content="Bonjour à tous les M1 ILIADE ! N'hésitez pas à poster vos questions sur les TP ici. Bon courage pour les premiers modules !"
        )
    except Student.DoesNotExist or ForumChannel.DoesNotExist:
        pass

    # Événement : Examen de Développement Web Avancé
    try:
        dev_web = courses.get(name="Développement Web Avancé")
        Event.objects.create(
            course=dev_web,
            title="Examen - Développement Web Avancé",
            description="Examen final portant sur les frameworks Django et React.",
            # Utilisation d'une date proche (à ajuster si besoin)
            start_time='2025-11-20 09:00:00',
            end_time='2025-11-20 12:00:00',
            location="Amphi B"
        )
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

        # 3. Insertion des Cours
        if not Course.objects.exists():
            for data in INITIAL_COURSES_DATA:
                Course.objects.create(**data)
            print("✅ Cours initiaux insérés.")
            
        # Récupération des cours pour les FK
        all_courses = Course.objects.all()

        # 4. Insertion du Contenu Initial (Emails, Posts, Events)
        if all_students.exists() and all_channels.exists() and all_courses.exists() and not Email.objects.exists():
             create_initial_content(all_students, all_channels, all_courses)
             print("✅ Contenu initial (Email, Post, Event) inséré.")
             
    except OperationalError as e:
        # Ceci gère le cas où la BDD n'est pas encore complètement créée au moment du signal
        # print(f"Warning (OperationalError): {e}") # Décommenter pour debug
        pass