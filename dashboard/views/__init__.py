# Fichier : dashboard/views/__init__.py
# Expose toutes les fonctions de vues au niveau du package 'views'

from .auth import login_view, logout_view 
from .dashboard import dashboard_view
from .profile import profile_view
from .calendar import calendar
from .chat import chat_view
from .forum import forum_view