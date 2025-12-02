# Fichier : dashboard/views/chat.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from dashboard.models import Student, Email
from dashboard.forms import EmailForm
from .auth import get_session_user_data
import unicodedata

def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

@require_POST
def delete_email_view(request):
    user_data = get_session_user_data(request)
    if not user_data: return redirect('dashboard:login')
    try:
        student = Student.objects.get(student_id=user_data.get('student_id'))
    except Student.DoesNotExist: return redirect('dashboard:login')

    email_id = request.POST.get('email_id')
    if email_id:
        try:
            email = Email.objects.get(id=email_id)
            if email.is_draft and email.sender == student:
                email.delete()
            elif email.recipient == student:
                email.is_deleted_by_recipient = True
                email.save()
            return redirect(reverse('dashboard:chat') + '?box=inbox')
        except Email.DoesNotExist:
            pass
    return redirect(reverse('dashboard:chat') + '?box=inbox')


def chat_view(request):
    user_data = get_session_user_data(request)
    if not user_data: return redirect('dashboard:login')

    try:
        student = Student.objects.get(student_id=user_data.get('student_id'))
    except Student.DoesNotExist: return redirect('dashboard:login')

    unread_count = Email.objects.filter(recipient=student, is_read=False, is_deleted_by_recipient=False, is_draft=False).count()

    # --- GESTION DES ACTIONS ---
    if request.method == 'POST':
        form = EmailForm(request.POST)

        # 1. SAUVEGARDER BROUILLON
        if 'save_draft' in request.POST:
            if form.is_valid():
                draft = form.save(commit=False)
                draft.sender = student
                draft.is_draft = True
                draft.recipient = None
                draft.save()
                return redirect(reverse('dashboard:chat') + '?box=drafts')

        # 2. ENVOYER LE MAIL
        elif 'send_email' in request.POST:
            if form.is_valid():
                # On récupère les destinataires
                recipients = form.cleaned_data.get('recipients')

                if not recipients:
                    # Erreur si aucun destinataire
                    form.add_error('recipients', "Veuillez choisir au moins un destinataire.")
                else:
                    # Envoi individuel à chaque destinataire sélectionné
                    subject = form.cleaned_data['subject']
                    body = form.cleaned_data['body']

                    for target in recipients:
                        Email.objects.create(
                            sender=student,
                            recipient=target,
                            subject=subject,
                            body=body,
                            is_draft=False
                        )
                    return redirect(reverse('dashboard:chat') + '?box=sent')
    else:
        form = EmailForm()

    # --- AFFICHAGE ---
    box_type = request.GET.get('box', 'inbox')

    if box_type == 'sent':
        emails = Email.objects.filter(sender=student, is_draft=False).select_related('recipient').order_by('-sent_at')
    elif box_type == 'trash':
        emails = Email.objects.filter(recipient=student, is_deleted_by_recipient=True).select_related('sender').order_by('-sent_at')
    elif box_type == 'drafts':
        emails = Email.objects.filter(sender=student, is_draft=True).order_by('-sent_at')
    else:
        emails = Email.objects.filter(recipient=student, is_deleted_by_recipient=False, is_draft=False).select_related('sender').order_by('-sent_at')

    # --- RECHERCHE ---
    search_query = request.GET.get('search', '')
    if search_query:
        all_emails = list(emails)
        emails = []
        query_clean = remove_accents(search_query.lower())
        for email in all_emails:
            sub = remove_accents(email.subject.lower())
            bod = remove_accents(email.body.lower())
            sen = remove_accents(email.sender.full_name.lower())
            rec = remove_accents(email.recipient.full_name.lower()) if email.recipient else ""

            if (query_clean in sub or query_clean in bod or query_clean in sen or query_clean in rec):
                emails.append(email)

    # --- SÉLECTION ---
    selected_email_id = request.GET.get('email_id')
    selected_email = None

    if selected_email_id:
        try:
            selected_email = Email.objects.get(id=selected_email_id)
            if selected_email.sender != student and selected_email.recipient != student:
                selected_email = None

            if selected_email and selected_email.recipient == student and not selected_email.is_read and box_type == 'inbox':
                selected_email.is_read = True
                selected_email.save()
                if unread_count > 0: unread_count -= 1
        except Email.DoesNotExist: pass
    elif emails:
        selected_email = emails[0]

    context = {
        'user': user_data,
        'emails': emails,
        'selected_email': selected_email,
        'box_type': box_type,
        'form': form,
        'search_query': search_query,
        'unread_count': unread_count
    }
    return render(request, 'chat.html', context)