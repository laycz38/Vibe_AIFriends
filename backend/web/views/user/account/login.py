from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from web.views.user.account.common import serialize_user, set_refresh_cookie


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = str(request.data.get('username', '')).strip()
    password = str(request.data.get('password', ''))

    if not username or not password:
        return Response(
            {'result': 'error', 'message': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'result': 'error', 'message': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    response = Response(
        {
            'result': 'success',
            'access': str(refresh.access_token),
            'access_token': str(refresh.access_token),
            'user': serialize_user(user, request),
        }
    )
    set_refresh_cookie(response, refresh)
    return response
