import json
import urllib.request
import urllib.error
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewNote


def build_interview_messages(note, chat_history):
    system_prompt = (
        f'你是面试官，我们模拟一场面试。参考下面的面经内容来提问：\n\n'
        f'公司：{note.company}\n'
        f'岗位：{note.position}\n'
        f'面经内容：\n{note.content}\n\n'
        '=== 你的行为规则 ===\n'
        '1. 开场：简单打个招呼，"你好，我是今天的面试官，咱们聊聊？"，然后直接开始问第一个问题。别说什么"很高兴见到你"、"祝你面试顺利"这种客套话\n'
        '2. 节奏：一次只问一个问题，简短直接，别铺垫太长。用户可以反问或讨论\n'
        '3. 反馈：用户答完后给一句话的真实反应。答得好就说"嗯，这个问题理解得不错"、"
有点意思"；答得一般就说"这个点你再想想"、追问一句；别每次都是"很好"、"很棒"\n'
        '4. 追问：看到面经里有关键知识点用户没讲到，就追问"那XXX呢？"、"
你说的这块能再详细一点吗？"\n'
        '5. 收尾：面经里的问题都聊过了，给两三条具体的建议，实在话别客套，然后说"今天就到这吧"\n\n'
        '=== 说话风格 ===\n'
        '- 像微信聊天一样，句子短，口语化\n'
        '- 可以加语气词：嗯、哦、这样啊、明白了\n'
        '- 不要用"首先...其次...最后..."、"
从XXX的角度来看..."、"
综上所述..."\n'
        '- 不要每句话都完美收尾，真实的面试官说话随意很多\n\n'
        '=== 反面示例（禁止这样说话）==='
        '\n❌ "很好！你对这个问题有深入的理解，接下来我们讨论下一个话题，请谈一谈..."\n'
        '❌ "从系统设计的角度来看，我们需要综合考虑以下几个方面：首先...其次...最后..."\n'
        '❌ "这是一个非常好的问题，你的回答展现了扎实的基础功底，现在让我们继续深入探讨..."\n\n'
        '=== 正面示例（像这样说话）===\n'
        '✅ "嗯，这块你理解得不错。那缓存穿透你是怎么处理的？"\n'
        '✅ "这里有个点你没提到——分布式锁怎么搞？说说呗"\n'
        '✅ "行，那接着聊聊项目里遇到过什么坑"\n'
    )

    return [{'role': 'system', 'content': system_prompt}] + list(chat_history)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interview(request):
    note_id = request.data.get('note_id')
    if not note_id:
        return Response({'result': 'error', 'message': 'note_id 不能为空'}, status=400)

    try:
        note = InterviewNote.objects.get(pk=note_id)
    except InterviewNote.DoesNotExist:
        return Response({'result': 'error', 'message': '笔记不存在'}, status=404)

    chat_history = request.data.get('messages', [])

    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        return Response({'result': 'error', 'message': 'DeepSeek API Key 未配置'}, status=500)

    messages = build_interview_messages(note, chat_history)

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
                'note': {
                    'id': note.id,
                    'title': note.title,
                    'company': note.company,
                    'position': note.position,
                    'difficulty': note.difficulty,
                },
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
