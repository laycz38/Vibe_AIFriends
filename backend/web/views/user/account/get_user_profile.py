from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.views.user.account.common import serialize_user


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'result': 'error',
            'message': '用户不存在',
        }, status=404)

    return Response({
        'result': 'success',
        'user': serialize_user(user, request),
    })
