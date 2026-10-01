"""The smallest complete request, with no helpers, so you can see the whole shape.

    uv run --env-file .env examples/01_hello.py
"""

import base64
from pathlib import Path

from google import genai

client = genai.Client()  # reads GEMINI_API_KEY

interaction = client.interactions.create(
    model="gemini-3.8-flash-tts",
    input=[{
        "type": "user_input",
        "content": [{
            "type": "text",
            "text": "Hello! This is Gemini 3.8 Flash TTS. Have a wonderful day!",  # spoken verbatim
            "annotations": [{
                "type": "speech_metadata",
                "style": "cheerful and friendly",  # how to say it (never spoken)
            }],
        }],
    }],
    response_format={"type": "audio"},  # unary default: complete WAV, 24 kHz mono 16-bit
    generation_config={
        "speech_config": [{"voice": "Kore"}],  # list = single speaker
    },
)

out = Path(__file__).resolve().parent.parent / "out"
out.mkdir(exist_ok=True)
# The audio already has a RIFF header, so write it straight to .wav.
(out / "01_hello.wav").write_bytes(base64.b64decode(interaction.output_audio.data))
print("wrote out/01_hello.wav")
