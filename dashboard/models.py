# Fichier : dashboard/models.py
from django.db import models
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Student(models.Model):
    """
    Modèle représentant un étudiant dans la base de données.
    Django gère automatiquement la connexion SQLite pour vous.
    """
    student_id = models.CharField(max_length=10, primary_key=True, verbose_name="Numéro d'Étudiant")
    email = models.EmailField(verbose_name="Adresse Email")
    full_name = models.CharField(max_length=100, verbose_name="Nom Complet")
    year = models.CharField(max_length=10, verbose_name="Niveau d'Études")
    # Pour un projet réel, utilisez un hachage sécurisé (ex: Django's User model).
    password_clear = models.CharField(max_length=50, verbose_name="Mot de passe (Clear Text)")
    
    def __str__(self):
        return f"{self.full_name} ({self.student_id})"

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

# --- Logique d'initialisation des données (pour simuler init_db) ---
@receiver(post_migrate)
def create_initial_students(sender, **kwargs):
    """
    Crée les comptes initiaux après les migrations.
    """
    # S'assurer que le signal ne s'exécute que pour l'application 'dashboard'
    if sender.name != 'dashboard':
        return

    try:
        if not Student.objects.exists():
            INITIAL_STUDENTS_DATA = [
                {"student_id": "22204565", "email": "simon.dumas@hub.fr", "full_name": "Simon DUMAS", "year": "M1", "password_clear": "1234"},
                {"student_id": "22204566", "email": "marie.dupont@hub.fr", "full_name": "Marie DUPONT", "year": "L3", "password_clear": "SecurePass456"},
                {"student_id": "22204567", "email": "alex.lefevre@hub.fr", "full_name": "Alex LEFEVRE", "year": "M2", "password_clear": "MySecret789"},
            ]
            for data in INITIAL_STUDENTS_DATA:
                Student.objects.create(**data)
            print("Données initiales des étudiants insérées via le modèle Django.")
    except OperationalError:
        # Ignore si la table n'existe pas encore
        pass