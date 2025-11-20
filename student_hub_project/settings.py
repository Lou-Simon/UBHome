# Fichier : student_hub_project/settings.py (Modifications)
# ...
# Au début du fichier, on s'assure d'avoir la variable BASE_DIR
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# ...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # <-- FIX: Définit l'utilisation de SQLite
        'NAME': BASE_DIR / 'db.sqlite3',        # <-- Nomme le fichier de base de données
    }
}
# ...

# AJOUTEZ CETTE LIGNE :
DEBUG = True 


# DOIT ÊTRE UNE LONGUE CHAÎNE ALÉATOIRE
SECRET_KEY = 'votre-clé-secrète-aléatoire-super-longue-et-unique-pour-votre-projet-mvc-ubo'

# ... (le reste de vos configurations)

# Définit le fichier qui contient la configuration URL racine
ROOT_URLCONF = 'student_hub_project.urls'

# Configuration des fichiers statiques (CSS, JS, images, etc.)
STATIC_URL = 'static/'

# --- AJOUT: configuration des médias (upload des pièces jointes) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AUTORISER LES HÔTES LOCAUX POUR LE DÉVELOPPEMENT :
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# DANS la section INSTALLED_APPS (vers la ligne 33)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions', # ESSENTIEL pour la gestion de session
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 1. Ajouter votre application ici
    'dashboard', 
]
# ...

# DANS la section MIDDLEWARE (vers la ligne 45)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # Doit être là pour la gestion de session (essentiel pour la connexion)
    'django.contrib.sessions.middleware.SessionMiddleware', 
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Celles-ci étaient manquantes ou mal placées :
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <-- FIX: Gère l'état de connexion de l'utilisateur
    'django.contrib.messages.middleware.MessageMiddleware',     # <-- FIX: Gère les messages système (erreurs, succès)
    
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ...

# DANS la section TEMPLATES (vers la ligne 59)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # <-- CLÉ MANQUANTE
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # <-- Configuré pour pointer vers votre dossier 'templates/'
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# ...

# --- Fuseau horaire: Europe/Paris ---
TIME_ZONE = 'Europe/Paris'
USE_TZ = True

# Ajoutez ceci à la fin du fichier si vous ne le trouvez pas :
# Redirige les utilisateurs connectés vers la route 'dashboard'
LOGIN_REDIRECT_URL = '/'
# Redirige les utilisateurs non connectés vers la route 'login' si besoin
LOGIN_URL = '/login'