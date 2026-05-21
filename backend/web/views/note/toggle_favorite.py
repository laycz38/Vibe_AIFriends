from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote, InterviewNoteFavorite


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, note_id):
    note = get_object_or_404(InterviewNote, id=note_id)
    fav, created = InterviewNoteFavorite.objects.get_or_create(user=request.user, note=note)

    if created:
        return Response({'result': 'success', 'favorited': True})
    else:
        fav.delete()
        return Response({'result': 'success', 'favorited': False})
