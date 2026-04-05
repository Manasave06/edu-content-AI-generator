from gtts import gTTS
import base64
import os

def text_to_speech(text: str, lang: str = "en") -> str:
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_file = "temp_audio.mp3"
        tts.save(audio_file)
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        os.remove(audio_file)
        return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        return None

def get_audio_html(audio_base64: str, autoplay: bool = False) -> str:
    autoplay_str = "autoplay" if autoplay else ""
    return f"""
    <audio controls {autoplay_str} style="width:100%;border-radius:12px;margin:8px 0;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """

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
    "Chinese": "zh-CN",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Korean": "ko",
    "Italian": "it"
}