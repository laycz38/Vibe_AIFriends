from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def logout(request):
    token_str = request.COOKIES.get('refresh_token')
    if token_str:
        try:
            token = RefreshToken(token_str)
            token.blacklist()
        except Exception:
            pass

    response = Response({'result': 'success'})
    response.delete_cookie('refresh_token')
    return response
