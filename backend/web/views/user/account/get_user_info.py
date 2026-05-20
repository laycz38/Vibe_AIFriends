from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from web.views.user.account.common import serialize_user


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    return Response({
        'result': 'success',
        'user': serialize_user(request.user, request),
    }, status=status.HTTP_200_OK)
