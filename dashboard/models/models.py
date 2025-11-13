from django.db import models

# --- 1. Modèle Étudiant (L'utilisateur) ---
class Student(models.Model):
    """Modèle représentant un étudiant dans la base de données."""
    student_id = models.CharField(max_length=10, primary_key=True, verbose_name="Numéro d'Étudiant")
    email = models.EmailField(verbose_name="Adresse Email")
    full_name = models.CharField(max_length=100, verbose_name="Nom Complet")
    year = models.CharField(max_length=10, verbose_name="Niveau d'Études")
    password_clear = models.CharField(max_length=50, verbose_name="Mot de passe (Clear Text)")
    
    # PERMET L'AJOUT DYNAMIQUE DE COURS : Un étudiant peut s'inscrire à plusieurs cours, et un cours a plusieurs étudiants.
    enrolled_courses = models.ManyToManyField('Course', blank=True, related_name='students_enrolled', verbose_name="Cours Inscrits") 
    
    def __str__(self):
        return f"{self.full_name} ({self.student_id})"

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

# -----------------------------------------------------------------------------

# --- 2. Modèles Calendrier (Courses & Events) ---
class Course(models.Model):
    """Modèle représentant un cours disponible. De nouveaux cours peuvent être créés à tout moment."""
    name = models.CharField(max_length=100, verbose_name="Nom du Cours")
    teacher = models.CharField(max_length=100, blank=True, verbose_name="Professeur")
    
    def __str__(self):
        return f"{self.name} par {self.teacher}"

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"

class Event(models.Model):
    """Modèle représentant un événement ponctuel (examen, RDV). De nouveaux événements peuvent être ajoutés dynamiquement."""
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cours Associé")
    title = models.CharField(max_length=255, verbose_name="Titre de l'Événement")
    description = models.TextField(blank=True, verbose_name="Description")
    start_time = models.DateTimeField(verbose_name="Heure de Début")
    end_time = models.DateTimeField(verbose_name="Heure de Fin")
    location = models.CharField(max_length=100, blank=True, verbose_name="Lieu")
    
    def __str__(self):
        return f"{self.title} le {self.start_time.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['start_time']

# -----------------------------------------------------------------------------

# --- 3. Modèle Messagerie (Emails) ---
class Email(models.Model):
    """Modèle pour stocker un email. De nouveaux emails peuvent être créés à l'envoi."""
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sent_emails', verbose_name="Expéditeur")
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_emails', verbose_name="Destinataire")
    subject = models.CharField(max_length=255, verbose_name="Objet")
    body = models.TextField(verbose_name="Contenu")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    
    def __str__(self):
        return f"Email: {self.subject} de {self.sender.full_name} à {self.recipient.full_name}"

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"
        ordering = ['-sent_at'] 

# -----------------------------------------------------------------------------

# --- 4. Modèles Forum (Channel & Post) ---
class ForumChannel(models.Model):
    """Modèle représentant un canal de discussion (par filière). De nouveaux canaux peuvent être créés par un administrateur."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du Canal")
    description = models.TextField(blank=True, verbose_name="Description")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Canal de Forum"
        verbose_name_plural = "Canaux de Forum"

class ForumPost(models.Model):
    """Modèle représentant un message posté. De nouveaux messages sont créés par les utilisateurs."""
    channel = models.ForeignKey(ForumChannel, on_delete=models.CASCADE, related_name='posts', verbose_name="Canal")
    author = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='forum_posts', verbose_name="Auteur")
    content = models.TextField(verbose_name="Contenu du Message")
    posted_at = models.DateTimeField(auto_now_add=True, verbose_name="Date du Post")
    
    def __str__(self):
        return f"Post par {self.author.full_name} dans {self.channel.name}"

    class Meta:
        verbose_name = "Post de Forum"
        verbose_name_plural = "Posts de Forum"
        ordering = ['posted_at']