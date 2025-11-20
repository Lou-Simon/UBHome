# Fichier : dashboard/views/forum.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .auth import get_session_user_data
# Ajouts d'import pour les modèles
from ..models import Student, ForumChannel, ForumPost, ForumAttachment, ForumReaction
# --- Ajout: timezone pour formater en heure de Paris ---
from django.utils import timezone
import mimetypes


def forum_view(request):
    """Vue pour afficher la page du Forum et envoyer un message.
    Le canal par défaut est celui correspondant à l'année de l'étudiant connecté.
    """
    user_data = get_session_user_data(request)

    if not user_data:
        return redirect('dashboard:login')

    # Récupérer l'objet Student de l'utilisateur connecté
    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return redirect('dashboard:login')

    # Déterminer le canal par défaut en fonction de l'année de l'étudiant
    channel_name = student.year or user_data.get("year")

    # Crée/récupère le canal de l'année de l'étudiant (ex: "M1 ILIADE")
    channel, _ = ForumChannel.objects.get_or_create(
        name=channel_name,
        defaults={
            "description": f"Canal de discussion pour la promotion {channel_name}."
        }
    )

    # Gestion de l'envoi d'un message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content or request.FILES.getlist('attachments'):
            post = ForumPost.objects.create(channel=channel, author=student, content=content)
            # Gérer les pièces jointes
            for f in request.FILES.getlist('attachments'):
                ForumAttachment.objects.create(post=post, file=f, original_name=getattr(f, 'name', ''))
        return redirect('dashboard:forum')

    # Récupération des posts du canal
    posts = channel.posts.select_related('author').prefetch_related('attachments').order_by('posted_at')

    context = {
        'user': user_data,
        'title': 'Forum Étudiant',
        'channel': channel,
        'posts': posts,
    }

    return render(request, 'forum.html', context)


def forum_posts_json(request):
    """Retourne la liste des posts du canal par défaut de l'utilisateur au format JSON.
    Utilisé par le front pour rafraîchir les messages périodiquement sans recharger la page.
    """
    user_data = get_session_user_data(request)
    if not user_data:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    channel_name = student.year or user_data.get("year")
    channel, _ = ForumChannel.objects.get_or_create(
        name=channel_name,
        defaults={"description": f"Canal de discussion pour la promotion {channel_name}."}
    )

    posts_qs = channel.posts.select_related('author').prefetch_related('attachments', 'reactions__author').order_by('posted_at')

    posts = [
        {
            "id": p.id,
            "content": p.content,
            # Formate en heure locale (Europe/Paris via TIME_ZONE)
            "posted_at": timezone.localtime(p.posted_at).strftime('%d/%m/%Y %H:%M'),
            "author": {
                "student_id": p.author.student_id,
                "full_name": p.author.full_name,
            },
            "reactions": {
                reaction_type: {
                    "count": p.reactions.filter(emoji_type=reaction_type).count(),
                    "emoji": dict(ForumReaction.EMOJI_CHOICES)[reaction_type],
                    "user_reacted": p.reactions.filter(emoji_type=reaction_type, author=student).exists()
                }
                for reaction_type, _ in ForumReaction.EMOJI_CHOICES
                if p.reactions.filter(emoji_type=reaction_type).exists()
            },
            "user_reaction": p.reactions.filter(author=student).first().emoji_type if p.reactions.filter(author=student).exists() else None,
            "attachments": [
                {
                    "name": (att.original_name or att.file.name.split('/')[-1]),
                    "url": (att.file.url if hasattr(att.file, 'url') else ''),
                    "content_type": (mimetypes.guess_type(att.file.name)[0] or ''),
                    "size": getattr(att.file, 'size', None),
                }
                for att in p.attachments.all()
            ]
        }
        for p in posts_qs
    ]

    return JsonResponse({
        "channel": {"name": channel.name, "description": channel.description},
        "posts": posts,
    })


def toggle_reaction(request):
    """Vue pour ajouter/supprimer une réaction à un post"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    user_data = get_session_user_data(request)
    if not user_data:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    post_id = request.POST.get('post_id')
    emoji_type = request.POST.get('emoji_type')
    
    if not post_id or not emoji_type:
        return JsonResponse({"error": "Missing parameters"}, status=400)
    
    # Vérifier que l'emoji_type est valide
    valid_emojis = [choice[0] for choice in ForumReaction.EMOJI_CHOICES]
    if emoji_type not in valid_emojis:
        return JsonResponse({"error": "Invalid emoji type"}, status=400)
    
    try:
        post = ForumPost.objects.get(id=post_id)
    except ForumPost.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    
    # Vérifier si l'utilisateur a déjà une réaction sur ce post
    existing_reaction = ForumReaction.objects.filter(post=post, author=student).first()
    
    if existing_reaction:
        if existing_reaction.emoji_type == emoji_type:
            # Même réaction : supprimer
            existing_reaction.delete()
            action = "removed"
        else:
            # Réaction différente : modifier
            existing_reaction.emoji_type = emoji_type
            existing_reaction.save()
            action = "changed"
    else:
        # Pas de réaction existante : créer
        ForumReaction.objects.create(post=post, author=student, emoji_type=emoji_type)
        action = "added"
    
    return JsonResponse({"success": True, "action": action})