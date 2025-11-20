# dashboard/models.py
from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128) # Utilise un hacheur de mot de passe en production!
    year = models.CharField(max_length=20) # Année d'étude

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

class Email(models.Model):
    sender = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='received_emails')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    # NOUVEAU CHAMP ICI :
    is_deleted_by_recipient = models.BooleanField(default=False) # Ajoute cette ligne

    def __str__(self):
        return f"De {self.sender.full_name} à {self.recipient.full_name}: {self.subject}"

class ForumChannel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ForumPost(models.Model):
    channel = models.ForeignKey(ForumChannel, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author.full_name}"

class ForumAttachment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='forum_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name