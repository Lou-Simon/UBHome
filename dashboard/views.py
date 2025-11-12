# Fichier : dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Student # On importe le Modèle

# --- Fonctions utilitaires du Contrôleur ---

def get_session_user_data(request):
    """Récupère les données de l'étudiant à partir de la session."""
    student_id = request.session.get('student_id')
    if not student_id:
        return None
    try:
        # On utilise le Modèle (M) pour récupérer les données complètes
        student = Student.objects.get(student_id=student_id)
        return {
            "student_id": student.student_id,
            "full_name": student.full_name,
            "year": student.year,
            "email": student.email,
        }
    except Student.DoesNotExist:
        return None

# --- Points d'accès (Endpoints) ---

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Gère la connexion. Affiche la Vue 'login.html' (GET) ou traite le formulaire (POST)."""
    
    if request.session.get('student_id'):
        return redirect('dashboard') # Déjà connecté, on redirige
        
    if request.method == 'POST':
        # Traitement du formulaire JSON
        import json
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Format de requête invalide."}, status=400)
            
        try:
            # Appel au Modèle (M) : Recherche de l'étudiant
            student = Student.objects.get(student_id=student_id)
            
            # Vérification du mot de passe
            if student.password_clear == password:
                request.session['student_id'] = student.student_id # Création de la session
                return JsonResponse({
                    "full_name": student.full_name,
                    "year": student.year,
                    "student_id": student.student_id,
                    "email": student.email
                })
            else:
                return JsonResponse({"detail": "Numéro d'étudiant ou mot de passe incorrect."}, status=401)
                
        except Student.DoesNotExist:
            return JsonResponse({"detail": "Numéro d'étudiant ou mot de passe incorrect."}, status=401)
            
    # Requête GET: Affichage de la Vue (V) : login.html
    return render(request, 'login.html')

def dashboard_view(request):
    """Affiche le Tableau de Bord."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        return redirect('login') # Redirection si non authentifié
        
    # Rend la Vue (V) : dashboard.html
    return render(request, 'dashboard.html', {'user': user_data})


def profile_view(request):
    """Affiche la page de profil."""
    user_data = get_session_user_data(request)
    
    if not user_data:
        return redirect('login')
        
    # Appel au Modèle (M) : Récupération des détails pour la Vue
    student_details = get_object_or_404(Student, student_id=user_data['student_id'])
    
    # Rend la Vue (V) : profile.html
    return render(request, 'profile.html', {
        'student': student_details, 
        'user': user_data # Les données "user" sont toujours utiles pour la navigation
    })

def logout_view(request):
    """Déconnexion de l'utilisateur."""
    if 'student_id' in request.session:
        del request.session['student_id'] 
    return redirect('login')