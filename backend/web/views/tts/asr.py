import asyncio
import json
import os
import uuid

import websockets
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

WSS_URL = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asr_view(request):
    audio = request.FILES.get('audio')
    if not audio:
        return Response({'result': 'error', 'message': '音频不存在'}, status=400)

    pcm_data = audio.read()
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        return Response({'result': 'error', 'message': 'DASHSCOPE_API_KEY 未配置'}, status=500)

    try:
        text = asyncio.run(_run_asr(pcm_data, api_key))
        return Response({'result': 'success', 'text': text})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'result': 'error', 'message': str(e)}, status=500)


async def _asr_sender(pcm_data, ws, task_id):
    chunk = 3200
    for i in range(0, len(pcm_data), chunk):
        await ws.send(pcm_data[i: i + chunk])
        await asyncio.sleep(0.01)
    await ws.send(json.dumps({
        'header': {
            'action': 'finish-task',
            'task_id': task_id,
            'streaming': 'duplex',
        },
        'payload': {
            'input': {},
        },
    }))


async def _asr_receiver(ws):
    text = ''
    async for msg in ws:
        data = json.loads(msg)
        event = data['header']['event']
        if event == 'result-generated':
            output = data['payload']['output']
            transcription = output.get('transcription')
            if transcription and transcription.get('sentence_end'):
                text += transcription['text']
        elif event in ['task-finished', 'task-failed']:
            break
    return text


async def _run_asr(pcm_data, api_key):
    task_id = uuid.uuid4().hex
    headers = {'Authorization': f'Bearer {api_key}'}

    async with websockets.connect(WSS_URL, additional_headers=headers) as ws:
        await ws.send(json.dumps({
            'header': {
                'streaming': 'duplex',
                'task_id': task_id,
                'action': 'run-task',
            },
            'payload': {
                'model': 'gummy-realtime-v1',
                'parameters': {
                    'sample_rate': 16000,
                    'format': 'pcm',
                    'transcription_enabled': True,
                },
                'input': {},
                'task': 'asr',
                'task_group': 'audio',
                'function': 'recognition',
            },
        }))

        async for msg in ws:
            if json.loads(msg)['header']['event'] == 'task-started':
                break

        _, text = await asyncio.gather(
            _asr_sender(pcm_data, ws, task_id),
            _asr_receiver(ws),
        )
        return text
