from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote, InterviewNoteLike
from web.utils.cache import invalidate_note, invalidate_user_stats


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, note_id):
    note = get_object_or_404(InterviewNote, id=note_id)
    like, created = InterviewNoteLike.objects.get_or_create(user=request.user, note=note)

    if created:
        note.likes = F('likes') + 1
        note.save(update_fields=['likes'])
        note.refresh_from_db(fields=['likes'])
        invalidate_note(note_id)
        invalidate_user_stats(note.user_id)
        return Response({'result': 'success', 'liked': True, 'likes': note.likes})

    like.delete()
    note.likes = F('likes') - 1
    note.save(update_fields=['likes'])
    note.refresh_from_db(fields=['likes'])
    invalidate_note(note_id)
    invalidate_user_stats(note.user_id)
    return Response({'result': 'success', 'liked': False, 'likes': note.likes})
