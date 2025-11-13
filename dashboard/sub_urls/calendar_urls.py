# Fichier : dashboard/sub_urls/calendar_urls.py (Mise à jour)

from django.urls import path
# Importe DIRECTEMENT la fonction de vue 'calendar' du module '../views/calendar.py'
from ..views.calendar import calendar 

urlpatterns = [
    # Utilise la fonction 'calendar' directement
    path('', calendar, name='calendar'), 
]