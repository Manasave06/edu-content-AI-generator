import os
import base64
import tempfile

LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Korean": "ko",
    "Italian": "it",
}


def text_to_speech(text: str, lang: str = "en", max_chars: int = 2000) -> str:
    """Convert text to speech — longer audio support."""
    try:
        from gtts import gTTS
        text = text.strip()
        if not text:
            return None
        # Allow up to 2000 chars for longer audio
        text = text[:max_chars] if len(text) > max_chars else text

        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        try:
            os.unlink(tmp_path)
        except:
            pass
        return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        print(f"TTS error: {e}")
        return None


def get_audio_html(audio_base64: str, autoplay: bool = False) -> str:
    """Generate HTML audio player."""
    if not audio_base64:
        return ""
    autoplay_attr = "autoplay" if autoplay else ""
    return f"""
    <audio controls {autoplay_attr}
        style="width:100%;margin:8px 0;border-radius:8px;height:40px;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """