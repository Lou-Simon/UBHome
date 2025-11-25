# dashboard/models.py
from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) # Utilise un hacheur de mot de passe en production!
    year = models.CharField(max_length=20) # Année d'étude
    
    # NOUVEAU CHAMP : Photo de profil
    profile_picture = models.ImageField(
        upload_to='profile_pics/',    # Images stockées dans media/profile_pics/
        null=True,                    # Optionnel dans la BDD
        blank=True,                   # Optionnel dans les formulaires
        default='default_profile.png' # Image par défaut si aucune n'est uploadée
    )

    def __str__(self):
        return self.full_name

class Course(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    students = models.ManyToManyField(Student, related_name='courses')

    def __str__(self):
        return self.name

class Event(models.Model):
    # Nouveau champ pour le titre des événements personnels. 
    # Le nom du cours sera utilisé comme titre pour les événements académiques.
    title = models.CharField(max_length=200, default='Événement Personnel') 
    
    # Rend le champ course optionnel pour les événements personnels
    course = models.ForeignKey(
        'Course', 
        on_delete=models.SET_NULL, # Meilleure pratique : ne pas supprimer les événements si le cours est supprimé
        null=True, 
        blank=True
    ) 
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    
    # Nouveau champ pour lier l'événement aux étudiants participants (y compris l'organisateur)
    # Permet de lier l'événement à un ou plusieurs étudiants (Mael, vous-même, etc.)
    attendees = models.ManyToManyField('Student', related_name='events') 

    def __str__(self):
        # Utilise le titre ou le nom du cours pour l'affichage
        return self.title if self.course is None else f"Cours: {self.course.name}"

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"

# dashboard/models.py
# ... (Garde tes imports et les autres modèles Course, Event, Student...)

class Email(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sent_emails')
    
    # MODIFICATION : On autorise le destinataire à être vide (pour les brouillons)
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_emails', null=True, blank=True)
    
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_deleted_by_recipient = models.BooleanField(default=False)
    
    # AJOUT : Champ pour identifier un brouillon
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        if self.is_draft:
            return f"[BROUILLON] {self.subject}"
        # On gère le cas où recipient est None pour l'affichage
        recipient_name = self.recipient.full_name if self.recipient else "Inconnu"
        return f"De {self.sender.full_name} à {recipient_name}: {self.subject}"

# ... (Garde le reste : ForumChannel, etc.)

class ForumChannel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ForumPost(models.Model):
    channel = models.ForeignKey(ForumChannel, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField(blank=True)  # Rendre content optionnel
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content[:50]} by {self.author.full_name}"

class ForumAttachment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='forum_attachments/')
    original_name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name or self.file.name

class ForumReaction(models.Model):
    EMOJI_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😡'),
    ]
    
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='reactions')
    author = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reactions')
    emoji_type = models.CharField(max_length=10, choices=EMOJI_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'author')  # Un utilisateur ne peut avoir qu'une seule réaction par post
    
    def __str__(self):
        return f"{self.get_emoji_type_display()} by {self.author.full_name} on {self.post.title}"