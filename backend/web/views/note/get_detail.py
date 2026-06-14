from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models import InterviewNote
from web.utils.cache import cache_note_detail, CACHE_TTL_NOTE_DETAIL
from web.views.note.common import serialize_note


@api_view(['GET'])
@permission_classes([AllowAny])
def get_detail(request, note_id):
    cache_key = cache_note_detail(note_id)
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        current_user = request.user if request.user.is_authenticated else None
        # Re-check liked/favorited for current user (can't cache per-user state)
        if current_user and cached_response.get('note'):
            from web.models import InterviewNoteLike, InterviewNoteFavorite
            cached_response['note']['liked'] = InterviewNoteLike.objects.filter(
                user=current_user, note_id=note_id
            ).exists()
            cached_response['note']['favorited'] = InterviewNoteFavorite.objects.filter(
                user=current_user, note_id=note_id
            ).exists()
        return Response(cached_response)

    note = get_object_or_404(
        InterviewNote.objects.select_related('user').prefetch_related('comments__user'),
        id=note_id,
    )
    current_user = request.user if request.user.is_authenticated else None
    response_data = {
        'result': 'success',
        'note': serialize_note(note, request, current_user=current_user, include_comments=True),
    }

    cache.set(cache_key, response_data, timeout=CACHE_TTL_NOTE_DETAIL)

    return Response(response_data)
