# Fichier : dashboard/models/student_model.py (Définition du Modèle)

from django.db import models

class Student(models.Model):
    """Modèle représentant un étudiant dans la base de données."""
    student_id = models.CharField(max_length=10, primary_key=True, verbose_name="Numéro d'Étudiant")
    email = models.EmailField(verbose_name="Adresse Email")
    full_name = models.CharField(max_length=100, verbose_name="Nom Complet")
    year = models.CharField(max_length=10, verbose_name="Niveau d'Études")
    password_clear = models.CharField(max_length=50, verbose_name="Mot de passe (Clear Text)")
    
    def __str__(self):
        return f"{self.full_name} ({self.student_id})"

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"