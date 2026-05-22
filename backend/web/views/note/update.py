from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote
from web.views.image_utils import process_base64
from web.views.note.common import serialize_note


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, note_id):
    try:
        note = InterviewNote.objects.get(id=note_id)
    except InterviewNote.DoesNotExist:
        return Response({
            'result': 'error',
            'message': '笔记不存在',
        }, status=status.HTTP_404_NOT_FOUND)

    if note.user != request.user:
        return Response({
            'result': 'error',
            'message': '无权修改此笔记',
        }, status=status.HTTP_403_FORBIDDEN)

    note.title = request.data.get('title', note.title).strip()
    note.content = request.data.get('content', note.content).strip()
    note.company = request.data.get('company', note.company).strip()
    note.position = request.data.get('position', note.position).strip()

    difficulty = request.data.get('difficulty', '').strip()
    if difficulty in ('简单', '中等', '困难'):
        note.difficulty = difficulty

    cover = request.data.get('cover_base64', '').strip()
    if cover:
        note.cover_base64 = process_base64(cover)

    note.save()

    return Response({
        'result': 'success',
        'note': serialize_note(note, request),
    }, status=status.HTTP_200_OK)
