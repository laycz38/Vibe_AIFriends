from django.core.exceptions import ObjectDoesNotExist

from web.models import InterviewNoteComment, InterviewNoteFavorite, InterviewNoteLike, UserProfile


def build_avatar_url(profile, request):
    if profile and profile.photo_base64:
        return profile.photo_base64
    return ''


def serialize_comment(comment, request):
    try:
        profile = comment.user.userprofile
    except ObjectDoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=comment.user)
    return {
        'id': comment.id,
        'content': comment.content,
        'author': comment.user.username,
        'avatar': build_avatar_url(profile, request),
        'created_at': comment.created_at.isoformat(),
    }


def serialize_note(note, request, current_user=None, include_comments=False):
    try:
        profile = note.user.userprofile
    except ObjectDoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=note.user)

    image = note.cover_base64

    # Use annotated values when available (avoids N+1 queries)
    liked = getattr(note, 'liked', False)
    favorited = getattr(note, 'favorited', False)
    comment_count = getattr(note, 'comment_count', note.comments.count())

    data = {
        'id': note.id,
        'image': image,
        'title': note.title,
        'content': note.content,
        'author': note.user.username,
        'author_id': note.user.id,
        'avatar': build_avatar_url(profile, request),
        'likes': note.likes,
        'liked': liked,
        'favorited': favorited,
        'company': note.company,
        'position': note.position,
        'difficulty': note.difficulty,
        'comment_count': comment_count,
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat(),
    }

    if include_comments:
        comments = note.comments.select_related('user').all()
        data['comments'] = [serialize_comment(comment, request) for comment in comments]

    return data
