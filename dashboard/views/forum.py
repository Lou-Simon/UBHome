# Fichier : dashboard/views/forum.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .auth import get_session_user_data
from ..models import Student, ForumChannel, ForumPost, ForumAttachment
import mimetypes


def forum_view(request):
    user_data = get_session_user_data(request)
    if not user_data:
        return redirect('dashboard:login')

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return redirect('dashboard:login')

    # Extraire niveau (M1) et filière (ILIADE, LSE, etc.)
    student_year = student.year or user_data.get("year") or "M1"
    parts = student_year.split()
    level = parts[0] if parts else "M1"  # Ex: "M1"
    filiere = parts[1] if len(parts) > 1 else None  # Ex: "ILIADE" ou None

    # Créer les canaux par défaut pour ce niveau et cette filière
    default_channels = [student_year]  # Canal principal (ex: "M1 ILIADE")
    
    # Canaux généraux du niveau (accessibles à tous du même niveau)
    default_channels.extend([
        f"{level} Général",
        f"{level} Cours",
        f"{level} Projets",
    ])
    
    # Si l'étudiant a une filière, créer aussi un canal spécifique filière
    if filiere:
        default_channels.append(f"{level} {filiere}")
    
    for name in default_channels:
        ForumChannel.objects.get_or_create(name=name, defaults={"description": name})

    selected_channel_name = request.GET.get('channel', student_year)
    channel = ForumChannel.objects.filter(name=selected_channel_name).first() or ForumChannel.objects.first()

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        files = request.FILES.getlist('attachments')
        if content or files:
            post = ForumPost.objects.create(channel=channel, author=student, content=content)
            for f in files:
                ForumAttachment.objects.create(post=post, file=f, original_name=getattr(f, 'name', ''))
        return redirect(f"{request.path}?channel={channel.name}")

    posts = channel.posts.select_related('author').prefetch_related('attachments').order_by('posted_at')

    # FILTRER: ne montrer que les canaux du niveau de l'étudiant (et éventuellement sa filière)
    all_user_channels = ForumChannel.objects.filter(name__startswith=level).order_by('name')
    
    # Si l'étudiant a une filière, on peut aussi filtrer pour ne montrer que:
    # - Les canaux généraux du niveau (M1 Général, M1 Cours, etc.)
    # - Les canaux de sa filière (M1 ILIADE)
    if filiere:
        # Montrer uniquement les canaux qui contiennent le niveau ET (pas de filière OU sa filière)
        filtered_channels = []
        for ch in all_user_channels:
            ch_parts = ch.name.split()
            # Garder si c'est un canal général (pas de filière spécifique) ou si c'est sa filière
            if len(ch_parts) == 1 or (len(ch_parts) == 2 and ch_parts[0] == level and (ch_parts[1] in ['Général', 'Cours', 'Projets'] or ch_parts[1] == filiere)):
                filtered_channels.append(ch)
            elif len(ch_parts) > 2 and ch_parts[0] == level and ch_parts[1] == filiere:
                # Canaux comme "M1 ILIADE xyz"
                filtered_channels.append(ch)
        all_user_channels = filtered_channels

    channels_with_counts = [
        {
            'channel': ch,
            'post_count': ch.posts.count(),
            'is_active': ch.id == channel.id,
            'unread_count': ch.posts.exclude(
                read_by__student=student
            ).exclude(author=student).count()  # Messages non lus (hors mes propres messages)
        }
        for ch in all_user_channels
    ]

    # Marquer les posts du canal actuel comme lus
    if channel:
        from ..models import ForumPostRead
        for post in posts:
            if post.author != student:  # Ne pas marquer ses propres messages
                ForumPostRead.objects.get_or_create(post=post, student=student)

    return render(
        request,
        'forum.html',
        {
            'user': user_data,
            'channel': channel,
            'posts': posts,
            'all_channels': channels_with_counts,
        },
    )


def forum_posts_json(request):
    """Version simple: juste les posts du canal au format JSON, sans réactions ni sondages."""
    user_data = get_session_user_data(request)
    if not user_data:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    selected_channel_name = request.GET.get('channel') or student.year or user_data.get("year")
    channel, _ = ForumChannel.objects.get_or_create(
        name=selected_channel_name,
        defaults={"description": selected_channel_name},
    )

    posts_qs = channel.posts.select_related('author').prefetch_related('attachments').order_by('posted_at')

    posts = [
        {
            "id": p.id,
            "content": p.content,
            "posted_at": timezone.localtime(p.posted_at).strftime('%d/%m/%Y %H:%M'),
            "author": {
                "student_id": p.author.student_id,
                "full_name": p.author.full_name,
            },
            "attachments": [
                {
                    "name": (att.original_name or att.file.name.split('/')[-1]),
                    "url": (att.file.url if hasattr(att.file, 'url') else ''),
                    "content_type": (mimetypes.guess_type(att.file.name)[0] or ''),
                    "size": getattr(att.file, 'size', None),
                }
                for att in p.attachments.all()
            ],
        }
        for p in posts_qs
    ]

    return JsonResponse({"channel": {"name": channel.name, "description": channel.description}, "posts": posts})