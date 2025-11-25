# dashboard/forms.py
from django import forms
from .models import Email, Student

class EmailForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        required=False,
        label="Étudiants spécifiques",
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue h-32'
        })
    )

    group = forms.ChoiceField(
        choices=[],
        required=False,
        label="Ou toute une filière",
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue'
        })
    )

    class Meta:
        model = Email
        fields = ['subject', 'body']
        widgets = {
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
        self.fields['recipients'].queryset = Student.objects.all()
        self.fields['recipients'].label_from_instance = lambda obj: f"{obj.full_name} ({obj.year})"
        
        distinct_years = Student.objects.order_by('year').values_list('year', flat=True).distinct()
        choices = [('', '--- Choisir une filière ---')] + [(year, year) for year in distinct_years if year]
        self.fields['group'].choices = choices

    # J'AI SUPPRIMÉ LA MÉTHODE clean() ICI.
    # La vérification "Destinataire obligatoire" se fera désormais dans la Vue, 
    # uniquement si on clique sur "Envoyer".