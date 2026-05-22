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
            if 'json' not in ct:
                return body

            # JSON response: extract audio
            data = json.loads(body.decode('utf-8'))
            audio_info = data.get('output', {}).get('audio')

            # audio_info is a dict with 'url' and 'data' fields
            if isinstance(audio_info, dict):
                # Try base64 data first
                if audio_info.get('data'):
                    return base64.b64decode(audio_info['data'])
                # Download from OSS URL
                audio_url = audio_info.get('url')
                if audio_url:
                    with urllib.request.urlopen(audio_url, timeout=15) as aud_resp:
                        return aud_resp.read()
                raise Exception(f'CosyVoice 音频无 data 也无 url: {data}')

            # audio_info is a plain base64 string
            if isinstance(audio_info, str) and audio_info:
                return base64.b64decode(audio_info)

            raise Exception(f'CosyVoice 返回格式无法解析: {data}')

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        raise Exception(f'CosyVoice API 错误 ({e.code}): {error_body}')
