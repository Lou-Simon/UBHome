from django.db import models
from django.utils import timezone # 👈 NÉCESSAIRE pour gérer les fuseaux horaires (Timezone-Aware)

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
    """Modèle représentant un événement ponctuel (examen, RDV)."""
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

    # ------------------------------------------------------------------
    # PROPRIÉTÉS AJOUTÉES POUR LE CALCUL DE POSITION DANS CALENDAR.HTML
    # ------------------------------------------------------------------
    
    @property
    def top_position_px(self):
        """Calcule la position verticale (top) en pixels pour l'événement.
        Base : 8h = 0px. Échelle : 100px par heure."""
        
        start_time_local = timezone.localtime(self.start_time)

        start_hour = start_time_local.hour
        
        # Si l'événement commence avant 8h (début de la grille)
        if start_hour < 8:
            return 0
        
        # Chaque minute vaut (100px / 60min) ≈ 1.666px
        start_minute_offset = start_time_local.minute * (100 / 60)
        
        # Calcul : (Heure de début - 8h) * 100px/heure + offset minutes
        return int((start_hour - 8) * 100 + start_minute_offset)

    @property
    def height_px(self):
        """Calcule la hauteur en pixels pour l'événement. 100px par heure."""
        duration = self.end_time - self.start_time
        # Duration en minutes * (100px / 60min)
        total_minutes = duration.total_seconds() / 60
        
        return int(total_minutes * (100 / 60))
        
# -----------------------------------------------------------------------------

# --- 3. Modèle Messagerie (Emails) ---
class Email(models.Model):
    """Modèle pour stocker un email."""
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
    """Modèle représentant un canal de discussion (par filière)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du Canal")
    description = models.TextField(blank=True, verbose_name="Description")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Canal de Forum"
        verbose_name_plural = "Canaux de Forum"

class ForumPost(models.Model):
    """Modèle représentant un message posté."""
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

# --- 4.bis. Pièces jointes des posts ---
class ForumAttachment(models.Model):
    """Fichier joint à un message de forum."""
    post = models.ForeignKey(ForumPost, related_name='attachments', on_delete=models.CASCADE, verbose_name="Post")
    file = models.FileField(upload_to='forum_attachments/', verbose_name="Fichier")
    original_name = models.CharField(max_length=255, blank=True, verbose_name="Nom d'origine")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ajouté le")

    def __str__(self):
        return self.original_name or (self.file.name.split('/')[-1] if self.file else 'Pièce jointe')

    class Meta:
        verbose_name = "Pièce jointe de Forum"
        verbose_name_plural = "Pièces jointes de Forum"