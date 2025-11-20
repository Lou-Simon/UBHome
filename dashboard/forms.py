# dashboard/forms.py
from django import forms
from .models import Email, Student

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={
                'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue',
                'placeholder': 'Sujet du message'
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue',
                'rows': 6,
                'placeholder': 'Votre message...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On affiche le nom complet des étudiants dans la liste déroulante
        self.fields['recipient'].queryset = Student.objects.all()
        self.fields['recipient'].label_from_instance = lambda obj: f"{obj.full_name} ({obj.student_id})"