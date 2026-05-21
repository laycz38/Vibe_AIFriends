import json
import urllib.request
import urllib.error
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    messages = request.data.get('messages', [])
    if not messages:
        return Response({'result': 'error', 'message': 'messages 不能为空'}, status=400)

    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        return Response({'result': 'error', 'message': 'DeepSeek API Key 未配置'}, status=500)

    req_body = json.dumps({
        'model': 'deepseek-chat',
        'messages': messages,
        'stream': False,
    }).encode('utf-8')

    http_req = urllib.request.Request(
        f'{settings.DEEPSEEK_BASE_URL}/v1/chat/completions',
        data=req_body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
    )

    try:
        with urllib.request.urlopen(http_req, timeout=60) as response:
            data = json.loads(response.read().decode('utf-8'))
            assistant_message = data['choices'][0]['message']
            return Response({
                'result': 'success',
                'message': assistant_message,
            })
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        return Response({
            'result': 'error',
            'message': f'DeepSeek API 错误 ({e.code}): {error_body}',
        }, status=502)
    except Exception as e:
        return Response({
            'result': 'error',
            'message': f'请求失败: {str(e)}',
        }, status=500)
