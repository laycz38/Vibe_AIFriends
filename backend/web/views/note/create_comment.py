from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote, InterviewNoteComment
from web.views.note.common import serialize_comment


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, note_id):
    note = get_object_or_404(InterviewNote, id=note_id)
    content = str(request.data.get('content', '')).strip()

    if not content:
        return Response(
            {'result': 'error', 'message': '评论内容不能为空'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    comment = InterviewNoteComment.objects.create(
        user=request.user,
        note=note,
        content=content,
    )

    return Response(
        {
            'result': 'success',
            'comment': serialize_comment(comment, request),
            'comment_count': note.comments.count(),
        },
        status=status.HTTP_201_CREATED,
    )
