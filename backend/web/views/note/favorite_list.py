from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNoteFavorite, InterviewNoteLike
from web.views.note.common import serialize_note


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorite_list(request):
    favorites = InterviewNoteFavorite.objects.filter(
        user=request.user
    ).select_related('note__user__userprofile').annotate(
        comment_count=Count('note__comments')
    ).order_by('-created_at')

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total = favorites.count()
    page_favs = favorites[start:end]

    note_ids = [fav.note_id for fav in page_favs]
    liked_ids = set(
        InterviewNoteLike.objects.filter(user=request.user, note_id__in=note_ids)
        .values_list('note_id', flat=True)
    )

    notes = []
    for fav in page_favs:
        note = fav.note
        note.liked = note.id in liked_ids
        note.favorited = True
        note.comment_count = fav.comment_count
        notes.append(serialize_note(note, request, current_user=request.user))

    return Response({
        'result': 'success',
        'notes': notes,
        'total': total,
        'page': page,
        'page_size': page_size,
    })
