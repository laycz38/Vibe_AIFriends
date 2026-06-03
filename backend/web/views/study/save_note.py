from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import StudyNote


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_note(request):
    page_url = str(request.data.get('page_url', '')).strip()
    content = str(request.data.get('content', ''))

    if not page_url:
        return Response({'result': 'error', 'message': 'page_url 不能为空'}, status=400)

    note, _ = StudyNote.objects.update_or_create(
        user=request.user,
        page_url=page_url,
        defaults={'content': content},
    )

    return Response({
        'result': 'success',
        'note': {
            'page_url': note.page_url,
            'content': note.content,
            'updated_at': note.updated_at.isoformat(),
        },
    })
