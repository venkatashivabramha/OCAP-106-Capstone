"""
Gemini TTS — text-to-speech for chat messages.
Uses gemini-2.0-flash-preview-tts (free tier). Returns base64 WAV audio.
"""
import requests, os, base64, struct, logging
from typing import Optional

logger = logging.getLogger(__name__)

GEMINI_TTS_MODEL = os.getenv('GEMINI_TTS_MODEL', 'gemini-2.0-flash-preview-tts')
API_KEY = os.getenv('GEMINI_API_KEY', '')
BASE = 'https://generativelanguage.googleapis.com/v1beta'


def _pcm_to_wav(pcm: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Wrap raw PCM bytes in a WAV header so browsers can play it."""
    data_size = len(pcm)
    header = b'RIFF'
    header += struct.pack('<I', 36 + data_size)
    header += b'WAVE'
    header += b'fmt '
    header += struct.pack('<IHHIIHH', 16, 1, channels, sample_rate,
                          sample_rate * channels * sample_width,
                          channels * sample_width, sample_width * 8)
    header += b'data'
    header += struct.pack('<I', data_size)
    return header + pcm


def generate_speech(text: str, voice_style: str = 'clear and friendly') -> Optional[str]:
    """
    Generate speech audio for a message.
    Returns base64-encoded WAV, or None if unavailable (caller should
    fall back to browser speech synthesis).
    """
    if not API_KEY:
        return None

    if len(text) > 800:
        text = text[:800]  # keep free-tier usage small

    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Say in a {voice_style} tone: {text}"
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": "Kore"}
                    }
                },
            },
        }
        url = f"{BASE}/models/{GEMINI_TTS_MODEL}:generateContent?key={API_KEY}"
        r = requests.post(url, json=payload, timeout=30)

        if r.status_code != 200:
            logger.warning(f"Gemini TTS error {r.status_code}: {r.text[:200]}")
            return None

        data = r.json()
        # Response contains inline audio data
        parts = data['candidates'][0]['content']['parts']
        for part in parts:
            inline = part.get('inlineData')
            if inline and inline.get('mimeType', '').startswith('audio/'):
                audio_bytes = base64.b64decode(inline['data'])
                # Gemini TTS returns raw PCM (audio/L16;rate=24000) — wrap in WAV
                if 'pcm' in inline['mimeType'] or inline['mimeType'] == 'audio/L16;rate=24000' or 'L16' in inline['mimeType']:
                    wav = _pcm_to_wav(audio_bytes)
                else:
                    wav = audio_bytes  # already a container format
                return base64.b64encode(wav).decode('utf-8')

        return None

    except Exception as e:
        logger.error(f"Gemini TTS exception: {e}")
        return None
