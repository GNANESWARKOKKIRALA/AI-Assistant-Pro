"""
voice/tts.py — Text-to-Speech using gTTS
Converts assistant response text to audio and returns base64 for playback.
"""
import io
import base64
from gtts import gTTS


def text_to_speech_base64(text: str, lang: str = "en") -> str:
    """
    Convert text to speech using gTTS.
    Returns a base64-encoded MP3 string ready for HTML audio embedding.
    """
    # Strip markdown-style formatting for cleaner audio
    clean_text = _clean_for_tts(text)
    tts = gTTS(text=clean_text, lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    audio_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return audio_b64


def _clean_for_tts(text: str) -> str:
    """Remove markdown artifacts that sound bad when read aloud."""
    import re
    # Remove source badge lines
    text = re.sub(r"📎 \*\*Sources:\*\*.*", "", text)
    # Remove bold/italic markers
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Remove inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove markdown links
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove heading hashes
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Collapse multiple newlines
    text = re.sub(r"\n{2,}", " ", text)
    return text.strip()


def get_audio_html(audio_b64: str) -> str:
    """Return an HTML audio element for autoplay (hidden controls)."""
    return f"""
    <audio controls style="width:100%;margin-top:6px;border-radius:8px;">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """
