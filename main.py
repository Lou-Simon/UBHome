import os
import sqlite3
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List

# --- Configuration de la Base de Données ---
DATABASE_FILE = "student_hub.db"

# Données brutes à insérer au démarrage si la base est vide
INITIAL_STUDENTS_DATA = [
    ("22204565", "simon.dumas@hub.fr", "Simon DUMAS", "M1", "1234"),
    ("22204566", "marie.dupont@hub.fr", "Marie DUPONT", "L3", "SecurePass456"),
    ("22204567", "alex.lefevre@hub.fr", "Alex LEFEVRE", "M2", "MySecret789")
]

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Modèle Pydantic pour la requête de connexion
class LoginRequest(BaseModel):
    student_id: str
    password: str

# --- Fonctions de Base de Données ---

def init_db():
    """Crée la table 'students' et insère les comptes initiaux si elle est vide."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Création de la table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                full_name TEXT NOT NULL,
                year TEXT NOT NULL,
                password_clear TEXT NOT NULL
            )
        """)
        
        # Vérification si des données existent déjà
        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] == 0:
            # Insertion des données brutes
            cursor.executemany("""
                INSERT INTO students (student_id, email, full_name, year, password_clear) 
                VALUES (?, ?, ?, ?, ?)
            """, INITIAL_STUDENTS_DATA)
            conn.commit()
            print("Données initiales des étudiants insérées en brut dans SQLite.")
        else:
            print("La table students existe déjà et contient des données.")
            
    except sqlite3.Error as e:
        print(f"Erreur SQLite lors de l'initialisation : {e}")
    finally:
        if conn:
            conn.close()

@app.on_event("startup")
def startup_event():
    """Initialise la base de données au démarrage de l'application."""
    init_db()

def find_student(student_id: str) -> Dict[str, Any] | None:
    """Recherche un étudiant dans la base de données par ID."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT student_id, email, full_name, year, password_clear FROM students WHERE student_id = ?", 
            (student_id,)
        )
        row = cursor.fetchone()
        
        if row:
            # Assurez-vous que l'ordre correspond à la sélection SQL
            return {
                "student_id": row[0],
                "email": row[1],
                "full_name": row[2],
                "year": row[3],
                "password_clear": row[4],
            }
        return None
    except sqlite3.Error as e:
        print(f"Erreur SQLite lors de la recherche de l'étudiant : {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Fonction utilitaire pour vérifier la "session" via les paramètres d'URL ---
def check_session(request: Request) -> Dict[str, str] | None:
    """Vérifie la présence des paramètres d'authentification dans l'URL (simule la session)."""
    student_id = request.query_params.get("student_id")
    full_name = request.query_params.get("name")
    year = request.query_params.get("year")
    email = request.query_params.get("email")

    if not all([student_id, full_name, year, email]):
        return None
    
    return {
        "student_id": student_id,
        "full_name": full_name,
        "year": year,
        "email": email
    }

# --- DEPENDANCE DE SÉCURITÉ (login_required) AMÉLIORÉE ---
def get_current_user(request: Request) -> Dict[str, str]:
    """
    Dépendance FastAPI pour vérifier l'authentification.
    Redirige vers /login en utilisant RedirectResponse si l'utilisateur n'est pas authentifié.
    """
    user_data = check_session(request)
    
    if not user_data:
        # 1. Crée une RedirectResponse
        response = RedirectResponse(url="/login", status_code=302)
        
        # 2. Utilise une HTTPException pour interrompre le flux et forcer la redirection
        # C'est la manière idiomatique de FastAPI de "sortir" d'une dépendance
        # en retournant une réponse HTTP complète.
        raise HTTPException(
            status_code=307, # 307 Temporary Redirect pour le bon comportement du navigateur
            detail="Non authentifié. Redirection...",
            headers={"Location": "/login"}
        )
    return user_data


# --- POINTS DE TERMINAISON (MAINTENANT PROTÉGÉS PAR DEPENDS) ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user_data: Dict[str, str] = Depends(get_current_user)):
    """
    Affiche la page du tableau de bord. Protégée par Depends(get_current_user).
    """
    # Si la dépendance réussit, user_data contient les infos de l'utilisateur
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "user": user_data}
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Affiche la page de connexion."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(login_data: LoginRequest):
    """Gère la soumission du formulaire de connexion."""
    student = find_student(login_data.student_id)
    
    if not student:
        raise HTTPException(status_code=401, detail="Numéro d'étudiant ou mot de passe incorrect.")
    
    # Vérification du mot de passe
    if student["password_clear"] == login_data.password:
        # Connexion réussie
        return {
            "full_name": student["full_name"],
            "year": student["year"],
            "student_id": student["student_id"],
            "email": student["email"]
        }
    else:
        # Mot de passe incorrect
        raise HTTPException(status_code=401, detail="Numéro d'étudiant ou mot de passe incorrect.")

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user_data: Dict[str, str] = Depends(get_current_user)):
    """
    Affiche la page de profil de l'étudiant connecté. Protégée par Depends.
    """
    # user_data est garanti d'être présent ici (sinon, get_current_user aurait redirigé)
    
    # Récupérer les données complètes de l'étudiant à partir de son ID dans la DB
    student_details = find_student(user_data["student_id"])

    if not student_details:
        # Ce cas ne devrait pas arriver si l'étudiant s'est connecté, mais c'est une bonne garde-fou
        raise HTTPException(status_code=404, detail="Profil étudiant non trouvé.")

    # Afficher la page de profil avec les données
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "student": student_details, "user": user_data}
    )

@app.get("/logout")
async def logout():
    """Redirige vers la page d'accueil sans les paramètres de session."""
    # Rediriger vers login "vide" la session (puisque les paramètres d'URL sont perdus)
    return RedirectResponse(url="/login", status_code=302)