import base64
import io
from PIL import Image


MAX_IMAGE_SIZE = (1200, 1200)
MAX_FILE_BYTES = 2 * 1024 * 1024


def _guess_format(raw):
    try:
        img = Image.open(io.BytesIO(raw))
        fmt = img.format
        return ('jpeg' if fmt == 'JPEG' else fmt).lower() if fmt else 'png'
    except Exception:
        return 'png'


def process_base64(raw_b64):
    if not raw_b64:
        return ''
    data = raw_b64.strip()
    if ',' in data:
        data = data.split(',', 1)[1]
    raw = base64.b64decode(data)
    if len(raw) > MAX_FILE_BYTES:
        raw = _resize(raw)
    ext = _guess_format(raw)
    b64 = base64.b64encode(raw).decode('utf-8')
    return f'data:image/{ext};base64,{b64}'


def _resize(raw):
    img = Image.open(io.BytesIO(raw))
    img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()
