# dashboard/views/chat.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from dashboard.models import Student, Email
from dashboard.forms import EmailForm
from .auth import get_session_user_data

@require_POST
def delete_email_view(request):
    user_data = get_session_user_data(request)
    if not user_data:
        # CORRECTION ICI : on ajoute 'dashboard:'
        return redirect('dashboard:login')

    try:
        student = Student.objects.get(student_id=user_data.get('student_id'))
    except Student.DoesNotExist:
        # CORRECTION ICI AUSSI
        return redirect('dashboard:login')

    email_id = request.POST.get('email_id')
    if email_id:
        try:
            email = Email.objects.get(id=email_id, recipient=student)
            email.is_deleted_by_recipient = True
            email.save()
            return redirect(reverse('dashboard:chat') + '?box=inbox')
        except Email.DoesNotExist:
            pass
    return redirect(reverse('dashboard:chat') + '?box=inbox')


def chat_view(request):
    user_data = get_session_user_data(request)
    if not user_data:
        # CORRECTION ICI : on ajoute 'dashboard:'
        return redirect('dashboard:login')

    try:
        student = Student.objects.get(student_id=user_data.get('student_id'))
    except Student.DoesNotExist:
        # CORRECTION ICI AUSSI
        return redirect('dashboard:login')

    # --- 1. Gestion du formulaire d'envoi (POST) ---
    if request.method == 'POST' and 'form_submit' in request.POST:
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.save(commit=False)
            email.sender = student
            email.save()
            base_url = reverse('dashboard:chat')
            return redirect(f'{base_url}?box=sent')
    else:
        form = EmailForm()

    # --- 2. Gestion de l'affichage ---
    box_type = request.GET.get('box', 'inbox')

    if box_type == 'sent':
        emails = Email.objects.filter(sender=student).select_related('recipient').order_by('-sent_at')
    else:
        emails = Email.objects.filter(recipient=student, is_deleted_by_recipient=False).select_related('sender').order_by('-sent_at')

    # --- 3. Gestion de l'email sélectionné ---
    selected_email_id = request.GET.get('email_id')
    selected_email = None

    if selected_email_id:
        try:
            selected_email = Email.objects.get(id=selected_email_id)
            
            is_sender = (selected_email.sender == student)
            is_recipient = (selected_email.recipient == student)

            if not (is_sender or (is_recipient and not selected_email.is_deleted_by_recipient)):
                selected_email = None
            
            if is_recipient and not selected_email.is_read:
                selected_email.is_read = True
                selected_email.save()

        except Email.DoesNotExist:
            pass
            
    elif emails.exists():
        selected_email = emails.first()

    context = {
        'user': user_data,
        'emails': emails,
        'selected_email': selected_email,
        'box_type': box_type,
        'form': form,
    }

    return render(request, 'chat.html', context)