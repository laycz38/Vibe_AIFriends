from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote
from web.views.note.common import serialize_note


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    title = str(request.data.get('title', '')).strip()
    content = str(request.data.get('content', '')).strip()
    company = str(request.data.get('company', '')).strip()
    position = str(request.data.get('position', '')).strip()
    difficulty = str(request.data.get('difficulty', '中等')).strip() or '中等'
    cover = request.FILES.get('cover')

    if not title or not content or not company or not position:
        return Response(
            {'result': 'error', 'message': '标题、内容、公司和岗位不能为空'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if difficulty not in {'简单', '中等', '困难'}:
        return Response(
            {'result': 'error', 'message': '难度参数不合法'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    note = InterviewNote.objects.create(
        user=request.user,
        title=title,
        content=content,
        cover=cover,
        company=company,
        position=position,
        difficulty=difficulty,
    )

    return Response(
        {'result': 'success', 'note': serialize_note(note, request, current_user=request.user)},
        status=status.HTTP_201_CREATED,
    )
