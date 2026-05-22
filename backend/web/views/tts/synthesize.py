import base64
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from web.utils.aliyun_tts import synthesize as aliyun_synthesize


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def synthesize_speech(request):
    text = request.data.get('text', '').strip()
    if not text:
        return Response({'result': 'error', 'message': 'text 不能为空'}, status=400)

    if len(text) > 2000:
        return Response({'result': 'error', 'message': 'text 过长（最多 2000 字符）'}, status=400)

    voice = request.data.get('voice', 'female')

    try:
        audio_data = aliyun_synthesize(text, voice)
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return Response({
            'result': 'success',
            'audio': audio_base64,
            'format': 'mp3',
        })
    except Exception as e:
        return Response({
            'result': 'error',
            'message': f'语音合成失败: {str(e)}',
        }, status=500)
