# dashboard/views/profile.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST # Nouveau : pour la vue d'upload
from .auth import get_session_user_data 
from ..models import Student # Import du modèle Student
from ..forms import ProfilePictureForm # Nouveau : Import du formulaire de photo


def profile_view(request):
    """Affiche la page de profil et le formulaire d'édition."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        # Redirection vers l'URL de connexion (nommée 'login' dans votre dashboard/urls.py)
        return redirect('dashboard:login')
        
    student_details = get_object_or_404(Student, student_id=user_data['student_id'])
    
    # CRÉATION DU FORMULAIRE :
    # Nous lions le formulaire à l'instance de l'étudiant pour qu'il puisse être mis à jour.
    form = ProfilePictureForm(instance=student_details)
    
    return render(request, 'profile.html', {
        'student': student_details, 
        'user': user_data,
        'form': form, # NOUVEAU : On passe le formulaire au template
    })


# NOUVELLE VUE : Upload de la photo de profil
@require_POST
def upload_profile_picture(request):
    """Gère l'upload et la sauvegarde de la photo de profil."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        return redirect('dashboard:login')

    # Récupérer l'étudiant dont le profil doit être mis à jour
    student_to_update = get_object_or_404(Student, student_id=user_data['student_id'])

    # Instancie le formulaire avec les données POST, les fichiers (request.FILES)
    # et lie l'instance à l'étudiant actuel pour mise à jour
    form = ProfilePictureForm(request.POST, request.FILES, instance=student_to_update)

    if form.is_valid():
        # Sauvegarde le fichier dans MEDIA_ROOT et met à jour le chemin dans la BDD
        form.save() 
        # Optionnel : Ajoutez ici un message de succès (via le framework messages de Django)
    
    # Rediriger vers la page de profil (GET request)
    return redirect('dashboard:profile')