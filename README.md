# UBhome – Student Hub (Projet M1 – Groupe de 4)

Site web complet pour une communauté étudiante – réalisé en **Django 5 + Python 3.12**  
Novembre 2025

## Fonctionnalités principales

- **Authentification complète** (inscription, login, logout, réinitialisation mot de passe)  
- **Profil utilisateur** avec photo personnalisée + modification  
- **Calendrier interactif** (création/édition/suppression d’événements, vue mois/semaine/jour)  
- **Système de messagerie 100 % fonctionnel**  
  - Messages privés  
  - Messages groupés  
  - Corbeille & brouillons  
  - Réponses directes  
- **Forum complet** (catégories, topics, posts, réponses, likes)  
- **Dashboard personnalisé** selon le rôle/utilisateur  
- Design responsive (Tailwind CSS)

## Technologies utilisées

| Technologie             | Usage                                  |
|-------------------------|----------------------------------------|
| Django 5                | Backend + templating                   |
| Django-allauth          | Authentification                       |
| PostgreSQL              | Base de données en prod (SQLite en dev)|
| Tailwind CSS            | Design moderne & responsive            |
| JavaScript vanilla      | Interactions calendrier & forum        |
| Git & GitHub            | Collaboration + CI/CD                  |

## Équipe 

| Membre          | Rôle principal                                                |
|-----------------|---------------------------------------------------------------|
| Lou Simon       | Backend + BDD, reflexion IHM, forum et dashboard              |
| Maël Bogaër     | Backend + BDD, reflexion IHM, system de mail et dashboard     |
| **Simon Dumas** | Backend + BDD, reflexion IHM, calendrier interactif et profil |



## Lancer le projet en local

```bash
# 1. Clone
git clone https://github.com/SimDms29/UBhome.git
cd UBhome

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate   # ou venv\Scripts\activate sur Windows

# 3. Install
pip install -r requirements.txt

# 4. Migrations
python manage.py migrate

# 5. Lancement
python manage.py runserver
