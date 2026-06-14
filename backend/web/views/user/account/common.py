from django.core.cache import cache

from web.models import InterviewNoteComment, InterviewNoteLike, InterviewNote, UserProfile
from web.utils.cache import cache_user_stats, CACHE_TTL_USER_STATS


def serialize_user(user, request):
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Try Redis cache for stats (hot path: called on every auth request)
    cache_key = cache_user_stats(user.id)
    cached_stats = cache.get(cache_key)
    if cached_stats is not None:
        return {
            'id': user.id,
            'username': user.username,
            'photo': profile.photo_base64,
            'bio': profile.bio,
            **cached_stats,
        }

    stats = {
        'note_count': InterviewNote.objects.filter(user=user).count(),
        'comment_count': InterviewNoteComment.objects.filter(user=user).count(),
        'like_count': InterviewNoteLike.objects.filter(user=user).count(),
    }
    cache.set(cache_key, stats, timeout=CACHE_TTL_USER_STATS)
    return {
        'id': user.id,
        'username': user.username,
        'photo': profile.photo_base64,
        'bio': profile.bio,
        **stats,
    }


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        samesite='Lax',
    )
