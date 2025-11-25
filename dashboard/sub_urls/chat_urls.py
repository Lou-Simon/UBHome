from django.urls import path
from dashboard.views import chat  # Assure-toi que l'import est bon

urlpatterns = [
    # La vue principale de la messagerie (http://.../chat/)
    path('', chat.chat_view, name='chat'),

    # La vue de suppression (http://.../chat/delete/)
    # C'est ICI qu'on ajoute la ligne manquante :
    path('delete/', chat.delete_email_view, name='delete_email'),
]