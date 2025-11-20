from django.contrib import admin
# On importe tes modèles depuis models.py
from .models import Student, Course, Event, Email, ForumChannel, ForumPost, ForumAttachment

# --- Configuration de l'affichage dans l'admin ---

# Pour les Étudiants
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'year')
    search_fields = ('full_name', 'email', 'student_id')

# Pour les Emails
@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('subject', 'body')

# Pour les Cours
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')

# Pour les Événements (Calendrier)
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'location')
    list_filter = ('course',)

# Pour le Forum
admin.site.register(ForumChannel)
admin.site.register(ForumPost)
admin.site.register(ForumAttachment)