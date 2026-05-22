import queue
import threading
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat, ResultCallback
from django.conf import settings

dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'

VOICE_MAP = {
    'female': 'longanhuan',  # 龙安欢 - 欢脱元气女声
    'male': 'longanyang',    # 龙安洋 - 阳光大男孩
}


def _make_synthesizer(voice_name):
    return SpeechSynthesizer(
        model='cosyvoice-v3-flash',
        voice=voice_name,
        format=AudioFormat.MP3_24000HZ_MONO_256KBPS,
    )


def synthesize(text, voice='female'):
    """Call DashScope CosyVoice via WebSocket SDK and return raw audio bytes (MP3)."""
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        raise Exception('DASHSCOPE_API_KEY not configured')

    dashscope.api_key = api_key
    voice_name = VOICE_MAP.get(voice, voice)
    synthesizer = _make_synthesizer(voice_name)
    audio_data = synthesizer.call(text)

    if not audio_data:
        raise Exception('CosyVoice 合成失败：未返回音频数据')

    return audio_data


def synthesize_stream(text, voice='female'):
    """Stream CosyVoice audio chunks via SDK callback. Generator yields bytes."""
    api_key = settings.DASHSCOPE_API_KEY
    if not api_key:
        raise Exception('DASHSCOPE_API_KEY not configured')

    dashscope.api_key = api_key
    voice_name = VOICE_MAP.get(voice, voice)

    chunk_queue = queue.Queue()

    class StreamCallback(ResultCallback):
        def on_data(self, data: bytes) -> None:
            chunk_queue.put(('data', data))

        def on_complete(self):
            chunk_queue.put(('done', None))

        def on_error(self, message: str):
            chunk_queue.put(('error', message))

    synthesizer = SpeechSynthesizer(
        model='cosyvoice-v3-flash',
        voice=voice_name,
        format=AudioFormat.MP3_24000HZ_MONO_256KBPS,
        callback=StreamCallback(),
    )

    def run():
        try:
            synthesizer.call(text)
        except Exception as e:
            chunk_queue.put(('error', str(e)))

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    while True:
        msg_type, data = chunk_queue.get()
        if msg_type == 'data':
            yield data
        elif msg_type == 'done':
            break
        elif msg_type == 'error':
            raise Exception(data)
