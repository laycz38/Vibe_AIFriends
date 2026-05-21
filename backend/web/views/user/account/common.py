from web.models import InterviewNoteComment, InterviewNoteLike, InterviewNote, UserProfile


def serialize_user(user, request):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return {
        'id': user.id,
        'username': user.username,
        'photo': profile.photo_base64,
        'bio': profile.bio,
        'note_count': InterviewNote.objects.filter(user=user).count(),
        'comment_count': InterviewNoteComment.objects.filter(user=user).count(),
        'like_count': InterviewNoteLike.objects.filter(user=user).count(),
    }


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        samesite='Lax',
    )
