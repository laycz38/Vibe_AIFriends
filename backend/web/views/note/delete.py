from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request, note_id):
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
            'message': '无权删除此笔记',
        }, status=status.HTTP_403_FORBIDDEN)

    note.delete()

    return Response({
        'result': 'success',
    }, status=status.HTTP_200_OK)
