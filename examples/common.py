"""Small helpers shared by the examples. Read 01_hello.py first: it shows the raw request."""

import base64
import json
import os
import wave
from pathlib import Path

from google import genai

# Both 3.8 TTS models share the same request schema, so switching is one env var.
MODEL = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts")
OUT = Path(__file__).resolve().parent.parent / "out"
OUT.mkdir(exist_ok=True)

SAMPLE_RATE = 24_000  # 24 kHz, mono, 16-bit PCM

client = genai.Client()  # reads GEMINI_API_KEY from the environment


VOICES = OUT / "voices.json"  # name -> voice_... ID for voices you created (per API-key project)


def load_voices() -> dict:
    return json.loads(VOICES.read_text()) if VOICES.exists() else {}


def store_voices(voices: dict) -> None:
    VOICES.write_text(json.dumps(voices, indent=2))


def forget_voice(voices: dict, name: str) -> None:
    """Delete a stored voice (ignoring one that is already gone) and update the cache."""
    try:
        client.voices.delete(id=voices[name])
    except Exception as e:
        if 404 not in (getattr(e, "status_code", None), getattr(e, "code", None)):
            raise
    del voices[name]
    store_voices(voices)
    print(f"deleted {name}")


def turn(text: str, style: str | None = None, speaker: str | None = None) -> dict:
    """One spoken turn. `text` is read verbatim; `style`/`speaker` go in speech_metadata."""
    meta = {"type": "speech_metadata"}
    if style:
        meta["style"] = style
    if speaker:
        meta["speaker"] = speaker
    return {"type": "text", "text": text, "annotations": [meta]}


def speak(turns: list[dict], speech_config, mime_type: str = "audio/wav", model: str = MODEL) -> bytes:
    """Run one unary TTS request and return the decoded audio bytes.

    speech_config is a LIST for one speaker ([{"voice": "Kore"}]) and an OBJECT
    for two speakers ({"speakers": [{"speaker": "Joe", "voice": "Puck"}, ...]}).
    """
    interaction = client.interactions.create(
        model=model,
        input=[{"type": "user_input", "content": turns}],
        response_format={"type": "audio", "mime_type": mime_type},
        generation_config={"speech_config": speech_config},
    )
    return base64.b64decode(interaction.output_audio.data)


def save(name: str, audio: bytes) -> Path:
    """Save unary output, which is already a complete WAV file (RIFF header included)."""
    path = OUT / name
    path.write_bytes(audio)
    print(f"wrote {path.relative_to(OUT.parent)}")
    return path


def save_pcm_as_wav(name: str, pcm: bytes) -> Path:
    """Wrap headerless L16 PCM (streaming output, or mime_type="audio/l16") in a WAV header."""
    path = OUT / name
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)
    print(f"wrote {path.relative_to(OUT.parent)}")
    return path
