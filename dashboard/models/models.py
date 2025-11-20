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
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='events')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

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