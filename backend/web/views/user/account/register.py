from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from web.models import UserProfile
from web.views.user.account.common import serialize_user, set_refresh_cookie


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = str(request.data.get('username', '')).strip()
    password = str(request.data.get('password', ''))
    password_confirm = str(request.data.get('password_confirm', ''))

    if not username or not password:
        return Response(
            {'result': 'error', 'message': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != password_confirm:
        return Response(
            {'result': 'error', 'message': '两次输入的密码不一致'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'result': 'error', 'message': '用户名已存在'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, password=password)
    UserProfile.objects.get_or_create(user=user)

    refresh = RefreshToken.for_user(user)
    response = Response(
        {
            'result': 'success',
            'access': str(refresh.access_token),
            'access_token': str(refresh.access_token),
            'user': serialize_user(user, request),
        },
        status=status.HTTP_201_CREATED,
    )
    set_refresh_cookie(response, refresh)
    return response
