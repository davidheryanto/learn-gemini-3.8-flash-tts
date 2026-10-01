"""Voice replication: clone a voice you own from two recordings by the same adult speaker.

1. reference.wav: 10-30 s of clean, natural speech.
2. consent.wav: the same speaker reading this exact sentence (en-US):
     "I am the owner of this voice and I consent to Google using this voice to
      create a synthetic voice model."
Record both on the same mic in a quiet room; 24 kHz mono 16-bit WAV is recommended.
For example: ffmpeg -i in.m4a -ar 24000 -ac 1 -sample_fmt s16 reference.wav

Per the announcement, replication in AI Studio is unavailable in Illinois, Texas, EEA, UK,
Switzerland, and India; check availability for your region.
The easiest path is AI Studio (https://aistudio.google.com/generate-speech); this is the API route.

    uv run --env-file .env examples/08_voice_replication.py reference.wav consent.wav
"""

import base64
import sys
from pathlib import Path

from common import MODEL, client, save, speak, turn

if len(sys.argv) != 3:
    sys.exit(__doc__)


def b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


voice = client.voices.create(
    store=True,  # False returns a stateless `voicekey_...` (voice.key) with a 7-day TTL
    voice={
        "model": MODEL,
        "type": "replicated",
        "display_name": "My replicated voice",
        "replicated": {
            "source_audio": {"mime_type": "audio/wav", "data": b64(sys.argv[1])},
            "consent_audio": {"mime_type": "audio/wav", "data": b64(sys.argv[2])},
        },
    },
)
print(f"created {voice.id}  (delete later with client.voices.delete(id=...))")

save("08_replicated.wav", speak(
    [turn("Hello! This audio was synthesized using my replicated voice.")],
    [{"voice": voice.id}],
))
