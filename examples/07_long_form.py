"""Long-form or custom-voice dialogue: one request per turn, then join the audio.

You need this when:
  - a script is longer than the 8,192-token input limit (audiobooks, long podcasts), or
  - a scene uses designed/replicated voices (single-request multi-speaker is prebuilt-only).

Ask for raw PCM (audio/l16) so the chunks join cleanly, then add one WAV header.
Any voice ID works here: prebuilt names, library IDs, or your `voice_...` IDs.

    uv run --env-file .env examples/07_long_form.py
"""

from common import save_pcm_as_wav, speak, turn

cast = {"NARRATOR": "Gacrux", "ROBOT": "Algenib"}  # swap in voice_... IDs from 06

script = [
    ("NARRATOR", "The station had been silent for three hundred years.", "slow, ominous"),
    ("ROBOT", "Power restored. <short pause> Hello? Is anyone... still here?", "monotone and flat"),
    ("NARRATOR", "No one answered. <sigh> But somewhere, a door creaked open.", None),
    ("ROBOT", "Oh. <gasp> Oh my. A VISITOR!", "high pitch, delighted"),
]

pause = b"\x00\x00" * int(24_000 * 0.35)  # 350 ms of silence between turns
pcm = bytearray()
for who, text, style in script:
    print(f"{who}: {text}")
    pcm += speak([turn(text, style=style)], [{"voice": cast[who]}], mime_type="audio/l16")
    pcm += pause

save_pcm_as_wav("07_scene.wav", bytes(pcm))
