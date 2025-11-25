# dashboard/forms.py
from django import forms
from .models import Email, Student

class EmailForm(forms.ModelForm):
    # On garde uniquement la sélection multiple
    recipients = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        required=False,
        label="Destinataires",
        widget=forms.SelectMultiple(attrs={
            'id': 'select-recipients',
            'placeholder': 'Saisissez un nom ou une promo...',
            'class': 'w-full' 
        })
    )

    class Meta:
        model = Email
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue',
                'placeholder': 'Objet'
            }),
            'body': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border-border-light dark:border-border-dark bg-surface-light dark:bg-surface-dark text-gray-900 dark:text-white focus:ring-ubo-blue focus:border-ubo-blue',
                'rows': 10,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuration pour l'autocomplétion (Nom :: Email :: Promo)
        self.fields['recipients'].queryset = Student.objects.all()
        self.fields['recipients'].label_from_instance = lambda obj: f"{obj.full_name} :: {obj.email} :: {obj.year}"