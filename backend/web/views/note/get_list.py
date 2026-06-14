from django.core.cache import cache
from django.db.models import Count, Exists, OuterRef, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models import InterviewNote, InterviewNoteFavorite, InterviewNoteLike
from web.utils.cache import cache_note_list, CACHE_TTL_NOTE_LIST
from web.views.note.common import serialize_note


@api_view(['GET'])
@permission_classes([AllowAny])
def get_list(request):
    search_query = request.GET.get('search_query', '').strip()
    user_id = request.GET.get('user_id', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    current_user = request.user if request.user.is_authenticated else None
    current_user_id = current_user.id if current_user else None

    # Try Redis cache for non-search requests
    if not search_query:
        cache_key = cache_note_list(page, page_size, current_user_id)
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)

    notes = InterviewNote.objects.select_related('user__userprofile')

    if current_user:
        notes = notes.annotate(
            liked=Exists(
                InterviewNoteLike.objects.filter(user=current_user, note=OuterRef('pk'))
            ),
            favorited=Exists(
                InterviewNoteFavorite.objects.filter(user=current_user, note=OuterRef('pk'))
            ),
        )

    notes = notes.annotate(comment_count=Count('comments'))

    if user_id:
        notes = notes.filter(user_id=int(user_id))

    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    notes = notes.order_by('-created_at')

    start = (page - 1) * page_size
    end = start + page_size

    total = notes.count()
    page_notes = notes[start:end]

    response_data = {
        'result': 'success',
        'notes': [serialize_note(n, request, current_user=current_user) for n in page_notes],
        'total': total,
        'page': page,
        'page_size': page_size,
    }

    # Cache non-search list results
    if not search_query:
        cache.set(cache_key, response_data, timeout=CACHE_TTL_NOTE_LIST)

    return Response(response_data)
