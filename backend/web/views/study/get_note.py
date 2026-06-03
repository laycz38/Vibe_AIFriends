from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import StudyNote


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_note(request):
    page_url = request.GET.get('page_url', '').strip()
    if not page_url:
        return Response({'result': 'error', 'message': 'page_url 不能为空'}, status=400)

    try:
        note = StudyNote.objects.get(user=request.user, page_url=page_url)
        return Response({
            'result': 'success',
            'note': {
                'page_url': note.page_url,
                'content': note.content,
                'updated_at': note.updated_at.isoformat(),
            },
        })
    except StudyNote.DoesNotExist:
        return Response({'result': 'success', 'note': None})
