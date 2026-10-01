"""Streaming: play audio as it is generated (voice agents, read-aloud features).

Streamed chunks are headerless L16 PCM (24 kHz, mono, 16-bit), so you can pipe
them to a player or concatenate them. Here we time the first chunk and save a WAV.

    uv run --env-file .env examples/04_streaming.py
    # Optional live playback (Linux):
    uv run --env-file .env examples/04_streaming.py --raw | aplay -f S16_LE -r 24000 -c 1
"""

import base64
import sys
import time

from common import MODEL, client, save_pcm_as_wav, turn

raw = "--raw" in sys.argv  # write raw PCM to stdout instead of a file

start = time.perf_counter()
stream = client.interactions.create(
    model=MODEL,
    input=[{"type": "user_input", "content": [turn(
        "Streaming lets you start playback before the whole sentence is synthesized. "
        "That's what keeps a voice agent feeling snappy.",
        style="calm, clear",
    )]}],
    response_format={"type": "audio"},
    generation_config={"speech_config": [{"voice": "Kore"}]},
    stream=True,
)

pcm = bytearray()
completed = False
for event in stream:
    if event.event_type == "error":  # stream errors arrive as events, not exceptions
        sys.exit(f"stream error: {event.error}")
    if event.event_type == "interaction.completed":
        completed = True
    if event.event_type == "step.delta" and event.delta.type == "audio" and event.delta.data:
        chunk = base64.b64decode(event.delta.data)
        if not pcm:
            print(f"first audio chunk after {time.perf_counter() - start:.2f}s", file=sys.stderr)
        pcm += chunk
        if raw:
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()

if not completed:
    sys.exit("stream ended without interaction.completed; audio may be truncated")
print(f"done: {len(pcm) / 2 / 24_000:.1f}s of audio in {time.perf_counter() - start:.2f}s", file=sys.stderr)
if not raw:
    save_pcm_as_wav("04_streamed.wav", bytes(pcm))
