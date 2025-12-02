# Fichier : dashboard/views/chat.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
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
    current_box = request.POST.get('current_box', 'inbox') # On récupère où on est

    if email_id:
        try:
            email = Email.objects.get(id=email_id)

            # Cas 1 : Suppression d'un brouillon (Toujours définitif)
            if email.is_draft and email.sender == student:
                email.delete()

            # Cas 2 : Suppression d'un mail reçu
            elif email.recipient == student:
                if email.is_deleted_by_recipient:
                    # Si DÉJÀ dans la corbeille -> Suppression DÉFINITIVE
                    email.delete()
                else:
                    # Sinon -> Déplacement vers la corbeille (Soft delete)
                    email.is_deleted_by_recipient = True
                    email.save()

            # Redirection vers la boîte où l'on était (ex: trash)
            return redirect(reverse('dashboard:chat') + f'?box={current_box}')

        except Email.DoesNotExist:
            pass
    return redirect(reverse('dashboard:chat') + f'?box={current_box}')


def chat_view(request):
    # ... (Le reste de la fonction chat_view reste EXACTEMENT le même qu'avant) ...
    # Copiez-collez le contenu de la fonction chat_view de votre fichier précédent
    # (Je ne le remets pas ici pour ne pas surcharger la réponse, il n'a pas changé)
    user_data = get_session_user_data(request)
    if not user_data: return redirect('dashboard:login')
    try:
        student = Student.objects.get(student_id=user_data.get('student_id'))
    except Student.DoesNotExist: return redirect('dashboard:login')

    # --- CALCUL DES NOTIFICATIONS ---
    unread_count = Email.objects.filter(
        recipient=student, is_read=False, is_deleted_by_recipient=False, is_draft=False
    ).count()

    draft_count = Email.objects.filter(sender=student, is_draft=True).count()
    total_email_notifs = unread_count + draft_count

    # --- TRAITEMENT FORMULAIRE ---
    if request.method == 'POST':
        if request.POST.get('action') == 'autosave_draft':
            draft_id = request.POST.get('draft_id')
            subject = request.POST.get('subject', '')
            body = request.POST.get('body', '')
            if not subject and not body: return JsonResponse({'status': 'empty'})
            if draft_id:
                try:
                    email = Email.objects.get(id=draft_id, sender=student, is_draft=True)
                    email.subject = subject; email.body = body; email.save()
                    return JsonResponse({'status': 'updated', 'id': email.id})
                except Email.DoesNotExist: pass
            email = Email.objects.create(sender=student, recipient=None, subject=subject, body=body, is_draft=True)
            return JsonResponse({'status': 'created', 'id': email.id})

        form = EmailForm(request.POST)
        if 'send_email' in request.POST:
            if form.is_valid():
                recipients = form.cleaned_data.get('recipients')
                subject = form.cleaned_data['subject']
                body = form.cleaned_data['body']
                draft_id = request.POST.get('draft_id')
                if not recipients: form.add_error('recipients', "Veuillez choisir au moins un destinataire.")
                else:
                    for target in recipients:
                        Email.objects.create(sender=student, recipient=target, subject=subject, body=body, is_draft=False)
                    if draft_id:
                        try: Email.objects.filter(id=draft_id, sender=student, is_draft=True).delete()
                        except: pass
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

    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        all_emails = list(emails)
        emails = []
        query_clean = remove_accents(search_query.lower())
        for email in all_emails:
            sub = remove_accents(email.subject.lower())
            bod = remove_accents(email.body.lower())
            sen = remove_accents(email.sender.full_name.lower())
            rec_name = email.recipient.full_name.lower() if email.recipient else ""
            rec = remove_accents(rec_name)
            if (query_clean in sub or query_clean in bod or query_clean in sen or query_clean in rec):
                emails.append(email)

    # Sélection
    selected_email_id = request.GET.get('email_id')
    selected_email = None
    if selected_email_id:
        try:
            selected_email = Email.objects.get(id=selected_email_id)
            is_sender = (selected_email.sender == student)
            is_recipient = (selected_email.recipient == student)
            if not (is_sender or is_recipient): selected_email = None
            if selected_email and is_recipient and not selected_email.is_read and box_type == 'inbox':
                selected_email.is_read = True; selected_email.save()
                if unread_count > 0: unread_count -= 1
                if total_email_notifs > 0: total_email_notifs -= 1
        except Email.DoesNotExist: pass
    elif emails: selected_email = emails[0]

    context = {'user': user_data, 'emails': emails, 'selected_email': selected_email, 'box_type': box_type, 'form': form, 'search_query': search_query, 'unread_count': unread_count, 'draft_count': draft_count, 'total_email_notifs': total_email_notifs}
    return render(request, 'chat.html', context)