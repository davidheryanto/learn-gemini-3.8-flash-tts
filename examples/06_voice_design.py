"""Voice design: describe a character in words, get back a reusable `voice_...` ID.

Put permanent traits (age, gender, timbre, accent) in the description. Keep
`style` for per-line emotion. Stored voices count against a 200-per-project limit
(1-year TTL), so this script caches the ID in out/voices.json and reuses it.

    uv run --env-file .env examples/06_voice_design.py            # create once, then speak
    uv run --env-file .env examples/06_voice_design.py --delete   # remove it from your project
"""

import base64
import sys

from common import client, forget_voice, load_voices, save, speak, store_voices, turn

NAME = "Warm British Astronomer"
DESCRIPTION = (
    "A warm, thoughtful astronomer in his late 60s with a gentle British accent, "
    "speaking with quiet wonder."
)
voices = load_voices()

if "--delete" in sys.argv:
    if NAME in voices:
        forget_voice(voices, NAME)
    sys.exit()

if NAME not in voices:
    created = client.voices.create(
        store=True,
        voice={
            "type": "prompted",  # no "model": Flash-Lite rejects it for voice design
            "display_name": NAME,
            "gender": "male",
            "language_code": "en-GB",
            "prompted": {"input": DESCRIPTION},
        },
    )
    voices[NAME] = created.id
    store_voices(voices)
    print(f"created {created.id}")
    if created.sample_audio and created.sample_audio.data:
        save("06_preview.wav", base64.b64decode(created.sample_audio.data))

voice_id = voices[NAME]
save("06_designed.wav", speak(
    [turn("Look out past the rings of Saturn. <short pause> Those faint photons left "
          "their source millions of years ago.", style="reflective and awe-inspired")],
    [{"voice": voice_id}],
))
