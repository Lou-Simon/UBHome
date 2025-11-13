# Fichier : dashboard/models/__init__.py

# Expose le modèle (obligatoire pour from .models import Student)
from .student_model import Student

# Importe le module de signaux pour s'assurer que les récepteurs sont chargés au démarrage de l'application.
from . import signals