import base64
import json
import urllib.request
import urllib.error
from django.conf import settings

VOICE_MAP = {
    'female': 'longanhuan',  # 龙安欢 - 欢脱元气女声
    'male': 'longanyang',    # 龙安洋 - 阳光大男孩
}


def synthesize(text, voice='female'):
    """Call DashScope CosyVoice TTS API and return raw audio bytes (MP3)."""
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        raise Exception('DASHSCOPE_API_KEY not configured')

    voice_name = VOICE_MAP.get(voice, voice)

    req_body = json.dumps({
        'model': 'cosyvoice-v3-flash',
        'input': {
            'text': text,
            'voice': voice_name,
            'format': 'mp3',
            'sample_rate': 24000,
        },
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer',
        data=req_body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            ct = resp.headers.get('Content-Type', '')
            if 'json' in ct:
                # JSON response: extract audio from output field
                data = json.loads(body.decode('utf-8'))
                audio_b64 = data.get('output', {}).get('audio')
                if audio_b64:
                    return base64.b64decode(audio_b64)
                raise Exception(f'CosyVoice 返回 JSON 但无音频: {data}')
            return body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        raise Exception(f'CosyVoice API 错误 ({e.code}): {error_body}')
