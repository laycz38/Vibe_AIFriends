from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from web.utils.aliyun_tts import synthesize_stream


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def synthesize_stream_view(request):
    text = request.data.get('text', '').strip()
    if not text:
        return Response({'result': 'error', 'message': 'text 不能为空'}, status=400)

    if len(text) > 2000:
        return Response({'result': 'error', 'message': 'text 过长'}, status=400)

    voice = request.data.get('voice', 'female')

    try:
        gen = synthesize_stream(text, voice)
        response = StreamingHttpResponse(gen, content_type='audio/mpeg')
        response['Cache-Control'] = 'no-cache'
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        detail = str(e)
        if 'DASHSCOPE_API_KEY' in detail:
            detail = 'DASHSCOPE_API_KEY 环境变量未配置，请在 backend/.env 中设置'
        return Response({'result': 'error', 'message': detail}, status=500)
