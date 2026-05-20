from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote, InterviewNoteLike


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, note_id):
    note = get_object_or_404(InterviewNote, id=note_id)
    like, created = InterviewNoteLike.objects.get_or_create(user=request.user, note=note)

    if created:
        note.likes = note.like_records.count()
        note.save(update_fields=['likes'])
        return Response({'result': 'success', 'liked': True, 'likes': note.likes})

    like.delete()
    note.likes = note.like_records.count()
    note.save(update_fields=['likes'])
    return Response({'result': 'success', 'liked': False, 'likes': note.likes})
