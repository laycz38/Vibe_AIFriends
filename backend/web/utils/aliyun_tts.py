import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat
from django.conf import settings

dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'

VOICE_MAP = {
    'female': 'longanhuan',  # 龙安欢 - 欢脱元气女声
    'male': 'longanyang',    # 龙安洋 - 阳光大男孩
}


def synthesize(text, voice='female'):
    """Call DashScope CosyVoice via WebSocket SDK and return raw audio bytes (MP3)."""
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        raise Exception('DASHSCOPE_API_KEY not configured')

    dashscope.api_key = api_key

    voice_name = VOICE_MAP.get(voice, voice)

    synthesizer = SpeechSynthesizer(
        model='cosyvoice-v3-flash',
        voice=voice_name,
        format=AudioFormat.MP3_24000HZ_MONO_256KBPS,
    )

    audio_data = synthesizer.call(text)

    if not audio_data:
        raise Exception('CosyVoice 合成失败：未返回音频数据')

    return audio_data
