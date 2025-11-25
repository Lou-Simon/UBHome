from django.http import JsonResponse
from .models import ForumChannel, ForumPost

def forum_posts_json(request):
    """Retourne les posts en JSON pour le rafraîchissement AJAX"""
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Non autorisé'}, status=401)
    
    channel = ForumChannel.objects.first()
    if not channel:
        return JsonResponse({'channel': None, 'posts': []})
    
    posts = ForumPost.objects.filter(channel=channel).select_related('author').prefetch_related('attachments').order_by('posted_at')
    
    posts_data = []
    for post in posts:
        # Transformer les réactions
        reactions_formatted = {}
        for emoji, student_ids in post.reactions.items():
            reactions_formatted[emoji] = {
                'count': len(student_ids),
                'user_reacted': student_id in student_ids
            }
        
        attachments_data = []
        for att in post.attachments.all():
            attachments_data.append({
                'name': att.file.name.split('/')[-1] if att.file else '',
                'url': att.file.url if att.file else '',
                'size': att.file.size if att.file else 0,
                'content_type': getattr(att.file.file, 'content_type', '') if hasattr(att.file, 'file') else ''
            })
        
        posts_data.append({
            'id': post.id,
            'content': post.content,
            'posted_at': post.posted_at.strftime('%d/%m/%Y %H:%M'),
            'author': {
                'student_id': post.author.student_id,
                'full_name': post.author.full_name
            },
            'attachments': attachments_data,
            'reactions': reactions_formatted
        })
    
    return JsonResponse({
        'channel': {
            'name': channel.name,
            'description': channel.description or ''
        },
        'posts': posts_data
    })

def forum_react(request, post_id):
    """Ajoute ou retire une réaction à un post"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Non autorisé'}, status=401)
    
    try:
        post = ForumPost.objects.get(id=post_id)
    except ForumPost.DoesNotExist:
        return JsonResponse({'error': 'Post non trouvé'}, status=404)
    
    emoji = request.POST.get('emoji', '').strip()
    
    # Liste des emojis autorisés
    valid_emojis = ['👍', '❤️', '😂', '🎉']
    if emoji not in valid_emojis:
        return JsonResponse({'error': 'Emoji invalide'}, status=400)
    
    # Vérifier si la réaction existe déjà
    if emoji in post.reactions and student_id in post.reactions.get(emoji, []):
        # Retirer la réaction
        post.remove_reaction(student_id, emoji)
        action = 'removed'
    else:
        # Ajouter la réaction
        post.add_reaction(student_id, emoji)
        action = 'added'
    
    return JsonResponse({'success': True, 'action': action, 'emoji': emoji})