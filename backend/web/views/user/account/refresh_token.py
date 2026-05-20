from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from web.views.user.account.common import serialize_user, set_refresh_cookie


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token_value = request.COOKIES.get('refresh_token')
    if not refresh_token_value:
        return Response(
            {'result': 'error', 'message': '未检测到 refresh_token'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        token = RefreshToken(refresh_token_value)
        user = User.objects.get(id=token['user_id'])
    except (TokenError, User.DoesNotExist, KeyError):
        return Response(
            {'result': 'error', 'message': 'refresh_token 已失效'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    new_refresh = RefreshToken.for_user(user)
    response = Response(
        {
            'result': 'success',
            'access': str(new_refresh.access_token),
            'access_token': str(new_refresh.access_token),
            'user': serialize_user(user, request),
        }
    )
    set_refresh_cookie(response, new_refresh)
    return response
