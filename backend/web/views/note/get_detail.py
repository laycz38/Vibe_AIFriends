from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.models import InterviewNote
from web.views.note.common import serialize_note


@api_view(['GET'])
@permission_classes([AllowAny])
def get_detail(request, note_id):
    note = get_object_or_404(
        InterviewNote.objects.select_related('user').prefetch_related('comments__user'),
        id=note_id,
    )
    current_user = request.user if request.user.is_authenticated else None
    return Response({
        'result': 'success',
        'note': serialize_note(note, request, current_user=current_user, include_comments=True),
    })
