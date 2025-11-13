# Fichier : dashboard/models/signals.py (Logique d'Initialisation des Données)

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.utils import OperationalError
from .student_model import Student # Importe le modèle depuis le même package

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

@receiver(post_migrate)
def create_initial_students(sender, **kwargs):
    """Crée les comptes initiaux après les migrations."""
    
    if sender.name != 'dashboard':
        return

    try:
        # Vérifie si le modèle existe et s'il est vide
        if not Student.objects.exists():
            for data in INITIAL_STUDENTS_DATA:
                Student.objects.create(**data)
            print("✅ Données initiales des étudiants insérées.")
    except OperationalError:
        # Ceci gère le cas où la BDD n'est pas encore complètement créée au moment du signal
        pass