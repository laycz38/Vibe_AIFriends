import json
import time
import urllib.request
import urllib.error
from django.conf import settings

TOKEN_CACHE = {'token': None, 'expires_at': 0}


def _get_token():
    """Get a temporary token from Aliyun NLS, cached to avoid redundant API calls."""
    now = int(time.time())
    if TOKEN_CACHE['token'] and now < TOKEN_CACHE['expires_at']:
        return TOKEN_CACHE['token']

    access_key_id = settings.ALIYUN_NLS_ACCESS_KEY_ID
    access_key_secret = settings.ALIYUN_NLS_ACCESS_KEY_SECRET
    if not access_key_id or not access_key_secret:
        raise Exception('ALIYUN_NLS_ACCESS_KEY_ID or ALIYUN_NLS_ACCESS_KEY_SECRET not configured')

    req_body = json.dumps({
        'accessKeyId': access_key_id,
        'accessKeySecret': access_key_secret,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://nls-meta.cn-shanghai.aliyuncs.com/api/v1/token',
        data=req_body,
        headers={'Content-Type': 'application/json'},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            token = data.get('token')
            if not token:
                raise Exception(f'获取阿里云 Token 失败: {data}')
            # Cache until 5 minutes before expiry
            expire_time = data.get('expire_time', now + 3600)
            TOKEN_CACHE['token'] = token
            TOKEN_CACHE['expires_at'] = expire_time - 300
            return token
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        raise Exception(f'阿里云 Token API 错误 ({e.code}): {error_body}')


VOICE_MAP = {
    'female': 'ailun',
    'male': 'aicheng',
}


def synthesize(text, voice='female'):
    """Call Aliyun NLS TTS API and return raw audio bytes (MP3)."""
    appkey = settings.ALIYUN_NLS_APPKEY
    if not appkey:
        raise Exception('ALIYUN_NLS_APPKEY not configured')

    token = _get_token()
    voice_name = VOICE_MAP.get(voice, voice)

    req_body = json.dumps({
        'appkey': appkey,
        'text': text,
        'format': 'mp3',
        'sample_rate': 16000,
        'voice': voice_name,
        'volume': 50,
        'speech_rate': 0,
        'pitch_rate': 0,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://nls-gateway.aliyuncs.com/stream/v1/tts',
        data=req_body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'token {token}',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        raise Exception(f'阿里云 TTS API 错误 ({e.code}): {error_body}')
