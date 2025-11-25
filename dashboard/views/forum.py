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
    Supporte plusieurs canaux de discussion par niveau.
    """
    user_data = get_session_user_data(request)

    if not user_data:
        return redirect('dashboard:login')

    # Récupérer l'objet Student de l'utilisateur connecté
    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return redirect('dashboard:login')

    # Déterminer le niveau de l'étudiant (ex: "M1 ILIADE" -> "M1")
    student_year = student.year or user_data.get("year") or "M1"
    level = student_year.split()[0] if student_year else "M1"

    # Récupérer le canal sélectionné (depuis l'URL ou par défaut l'année de l'étudiant)
    selected_channel_name = request.GET.get('channel', student_year)

    # Créer les canaux prédéfinis pour ce niveau s'ils n'existent pas
    default_channels = [
        {'name': student_year, 'description': f'Canal principal de la promotion {student_year}'},
        {'name': f'{level} ILIADE', 'description': f'{level} - Parcours ILIADE'},
        {'name': f'{level} LSE', 'description': f'{level} - Parcours Logiciels, Systèmes et Environnements'},
        {'name': f'📢 {level} Général', 'description': f'{level} - Discussions générales et annonces'},
        {'name': f'📚 {level} Cours', 'description': f'{level} - Questions et discussions sur les cours'},
        {'name': f'💼 {level} Projets', 'description': f'{level} - Collaborations et projets étudiants'},
        {'name': f'🎉 {level} Social', 'description': f'{level} - Événements, sorties et discussions informelles'},
        {'name': f'💡 {level} Aide', 'description': f'{level} - Entraide entre étudiants'},
    ]
    
    for channel_data in default_channels:
        ForumChannel.objects.get_or_create(
            name=channel_data['name'],
            defaults={'description': channel_data['description']}
        )

    # Récupérer UNIQUEMENT les canaux de ce niveau
    all_channels = ForumChannel.objects.filter(
        name__startswith=level
    ).order_by('created_at')

    # Récupérer le canal sélectionné
    channel = ForumChannel.objects.filter(name=selected_channel_name).first()
    if not channel:
        # Si le canal n'existe pas, utiliser le premier canal du niveau
        channel = all_channels.first()

    # Gestion de l'envoi d'un message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        files = request.FILES.getlist('attachments')
        
        # Autoriser l'envoi si contenu OU fichiers
        if content or files:
            # Créer le post avec le contenu (vide si seulement fichiers)
            post = ForumPost.objects.create(
                channel=channel, 
                author=student, 
                content=content if content else ''
            )
            # Gérer les pièces jointes
            for f in files:
                ForumAttachment.objects.create(post=post, file=f, original_name=getattr(f, 'name', ''))
        
        # Rediriger vers le même canal
        return redirect(f"{request.path}?channel={channel.name}")

    # Récupération des posts du canal
    posts = channel.posts.select_related('author').prefetch_related('attachments').order_by('posted_at')

    # Calculer le nombre de messages par canal pour les badges
    channels_with_counts = []
    for ch in all_channels:
        post_count = ch.posts.count()
        channels_with_counts.append({
            'channel': ch,
            'post_count': post_count,
            'is_active': ch.id == channel.id
        })

    context = {
        'user': user_data,
        'title': 'Forum Étudiant',
        'channel': channel,
        'posts': posts,
        'all_channels': channels_with_counts,
    }

    return render(request, 'forum.html', context)


def forum_posts_json(request):
    """Retourne la liste des posts du canal courant de l'utilisateur au format JSON.
    Le canal est déterminé par le paramètre ?channel=..., sinon on prend l'année/niveau par défaut.
    """
    user_data = get_session_user_data(request)
    if not user_data:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    # Récupérer le nom du canal demandé, sinon canal par défaut (année/niveau)
    selected_channel_name = request.GET.get('channel')
    if not selected_channel_name:
        selected_channel_name = student.year or user_data.get("year")

    channel, _ = ForumChannel.objects.get_or_create(
        name=selected_channel_name,
        defaults={"description": f"Canal de discussion pour {selected_channel_name}."}
    )

    posts_qs = channel.posts.select_related('author').prefetch_related('attachments', 'reactions__author').order_by('posted_at')

    posts = [
        {
            "id": p.id,
            "content": p.content,
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


def create_poll(request):
    """Vue pour créer un sondage"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    user_data = get_session_user_data(request)
    if not user_data:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Récupérer le canal actuel depuis le referer ou la session
    referer = request.META.get('HTTP_REFERER', '')
    channel_name = None
    
    # Extraire le nom du canal depuis l'URL referer
    if '?channel=' in referer:
        import urllib.parse
        parsed = urllib.parse.urlparse(referer)
        params = urllib.parse.parse_qs(parsed.query)
        if 'channel' in params:
            channel_name = params['channel'][0]
    
    # Si pas de canal dans l'URL, utiliser l'année de l'étudiant
    if not channel_name:
        channel_name = student.year or user_data.get("year")
    
    channel, _ = ForumChannel.objects.get_or_create(
        name=channel_name,
        defaults={"description": f"Canal de discussion pour {channel_name}."}
    )

    # Récupérer la question et les options
    question = request.POST.get('question', '').strip()
    options = []
    i = 0
    while f'options[{i}]' in request.POST:
        opt = request.POST.get(f'options[{i}]', '').strip()
        if opt:
            options.append(opt)
        i += 1
    
    if not question or len(options) < 2:
        return JsonResponse({"error": "Question et au moins 2 options requises"}, status=400)
    
    # Créer le post avec le sondage encodé en JSON
    import json
    poll_data = {
        "type": "poll",
        "question": question,
        "options": options,
        "votes": {}  # Format: {option_index: [student_id1, student_id2, ...]}
    }
    
    post = ForumPost.objects.create(
        channel=channel,
        author=student,
        content=json.dumps(poll_data)
    )
    
    return JsonResponse({"success": True, "post_id": post.id})


def vote_poll(request):
    """Vue pour voter dans un sondage"""
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
    option_index = request.POST.get('option_index')
    
    if not post_id or option_index is None:
        return JsonResponse({"error": "Missing parameters"}, status=400)
    
    try:
        post = ForumPost.objects.get(id=post_id)
    except ForumPost.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    
    # Décoder le sondage
    import json
    try:
        poll_data = json.loads(post.content)
        if poll_data.get('type') != 'poll':
            return JsonResponse({"error": "Not a poll"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid poll data"}, status=400)
    
    # Retirer l'ancien vote de l'utilisateur s'il existe
    for opt_idx, voters in poll_data.get('votes', {}).items():
        if str(student.student_id) in voters:
            voters.remove(str(student.student_id))
    
    # Ajouter le nouveau vote
    option_index = str(option_index)
    if option_index not in poll_data['votes']:
        poll_data['votes'][option_index] = []
    
    if str(student.student_id) not in poll_data['votes'][option_index]:
        poll_data['votes'][option_index].append(str(student.student_id))
    
    # Sauvegarder
    post.content = json.dumps(poll_data)
    post.save()
    
    return JsonResponse({"success": True})


def create_channel(request):
    """Vue pour créer un canal personnalisé"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    user_data = get_session_user_data(request)
    if not user_data:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        student = Student.objects.get(student_id=user_data["student_id"])
    except Student.DoesNotExist:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Récupérer les données du formulaire
    channel_name = request.POST.get('channel_name', '').strip()
    channel_description = request.POST.get('channel_description', '').strip()
    
    if not channel_name:
        return JsonResponse({"error": "Le nom du canal est requis"}, status=400)
    
    # Déterminer le niveau de l'étudiant
    student_year = student.year or user_data.get("year") or "M1"
    level = student_year.split()[0] if student_year else "M1"
    
    # Préfixer le nom avec le niveau pour le filtrage
    full_channel_name = f"{level} {channel_name}"
    
    # Vérifier si le canal existe déjà
    if ForumChannel.objects.filter(name=full_channel_name).exists():
        return JsonResponse({"error": "Un canal avec ce nom existe déjà"}, status=400)
    
    # Créer le canal
    channel = ForumChannel.objects.create(
        name=full_channel_name,
        description=channel_description or f"Canal personnalisé créé par {student.full_name}"
    )
    
    return JsonResponse({
        "success": True, 
        "channel_name": channel.name,
        "channel_id": channel.id
    })