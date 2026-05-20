from web.models import InterviewNoteComment, InterviewNoteLike, UserProfile


def build_avatar_url(profile, request):
    if profile and profile.photo:
        return request.build_absolute_uri(profile.photo.url)
    return ''


def serialize_comment(comment, request):
    profile, _ = UserProfile.objects.get_or_create(user=comment.user)
    return {
        'id': comment.id,
        'content': comment.content,
        'author': comment.user.username,
        'avatar': build_avatar_url(profile, request),
        'created_at': comment.created_at.isoformat(),
    }


def serialize_note(note, request, current_user=None, include_comments=False):
    profile, _ = UserProfile.objects.get_or_create(user=note.user)
    image = ''
    if note.cover:
        image = request.build_absolute_uri(note.cover.url)

    liked = False
    if current_user and current_user.is_authenticated:
        liked = InterviewNoteLike.objects.filter(user=current_user, note=note).exists()

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
        'company': note.company,
        'position': note.position,
        'difficulty': note.difficulty,
        'comment_count': note.comments.count(),
        'created_at': note.created_at.isoformat(),
        'updated_at': note.updated_at.isoformat(),
    }

    if include_comments:
        comments = note.comments.select_related('user').all()
        data['comments'] = [serialize_comment(comment, request) for comment in comments]

    return data
