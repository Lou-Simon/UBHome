from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
# Correction CRUCIALE d'import pour accéder au modèle
from ..models import Student 

# --- Fonctions utilitaires du Contrôleur ---

def get_session_user_data(request):
    """Récupère les données de l'étudiant à partir de la session."""
    student_id = request.session.get('student_id')
    if not student_id:
        return None
    try:
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
    """Gère la connexion."""
    if request.session.get('student_id'):
        return redirect('dashboard:dashboard')
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Format de requête invalide."}, status=400)
            
        try:
            student = Student.objects.get(student_id=student_id)
            
            if student.password == password:
                request.session['student_id'] = student.student_id
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
            
    return render(request, 'login.html')

def logout_view(request):
    """Déconnexion de l'utilisateur."""
    if 'student_id' in request.session:
        del request.session['student_id'] 
    return redirect('dashboard:login')