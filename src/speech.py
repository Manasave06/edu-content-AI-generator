import base64
import io
from gtts import gTTS

# Language codes mapping
LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Portuguese": "pt",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh",
    "Arabic": "ar",
    "Russian": "ru",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Urdu": "ur",
}


def text_to_speech(text: str, lang_code: str = "en") -> str | None:
    """
    Convert text to speech using gTTS.
    Returns base64-encoded audio string or None on failure.
    """
    try:
        if not text or not text.strip():
            return None

        # Limit text length to avoid very long audio
        text = text[:1000] if len(text) > 1000 else text

        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_data = base64.b64encode(audio_buffer.read()).decode("utf-8")
        return audio_data
    except Exception as e:
        print(f"TTS Error: {e}")
        return None


def get_audio_html(audio_base64: str, autoplay: bool = False) -> str:
    """
    Generate HTML audio player from base64-encoded audio.
    Supports autoplay parameter.
    """
    if not audio_base64:
        return ""

    autoplay_attr = "autoplay" if autoplay else ""

    return f"""
    <audio controls {autoplay_attr} style="width:100%;margin:8px 0;border-radius:12px;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """