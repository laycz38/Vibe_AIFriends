from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import UserProfile
from web.views.user.account.common import serialize_user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    bio = str(request.data.get('bio', '')).strip()
    photo = request.FILES.get('photo')

    profile.bio = bio
    if photo is not None:
        profile.photo = photo
    profile.save()

    return Response({
        'result': 'success',
        'user': serialize_user(request.user, request),
    }, status=status.HTTP_200_OK)
