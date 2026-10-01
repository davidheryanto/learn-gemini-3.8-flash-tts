"""Directing delivery: `style` for the whole turn, inline <tags> for moments.

Rule of thumb from the docs:
  - Sustained (emotion, pace, pitch, whispering)  -> speech_metadata.style
  - Point-in-time (laugh, sigh, pause)            -> <tag> inside the text
  - Emphasis                                       -> CAPITALS, commas, dashes, ...
Stage directions written into `text` ("Say cheerfully: ...") may be spoken aloud on 3.8.

    uv run --env-file .env examples/02_direction.py
"""

from common import save, speak, turn

VOICE = [{"voice": "Charon"}]

clips = {
    # 1. Plain: always try with no style first; most text needs none.
    "02a_plain.wav": turn("Oh uh, yeah I think... hm, so that's actually really interesting."),
    # 2. Turn-level style.
    "02b_whisper.wav": turn(
        "Don't move. Something is outside the tent.",
        style="whispered urgently",
    ),
    "02c_pace_pitch.wav": turn(
        "Ladies and gentlemen, the doors are now open, please find your seats!",
        style="speaking rapidly, high pitch, excited inflection",
    ),
    # 3. Inline vocal bursts and pauses.
    "02d_tags.wav": turn(
        "<cough> Thank you all for coming tonight! <throat-clearing> As I was saying... "
        "<short pause> the results are in. <long pause> We WON. <laugh>"
    ),
    # 4. Emphasis with capitals plus a sigh.
    "02e_emphasis.wav": turn(
        "It was a VERY long day <sigh> ... nobody listens anymore.",
        style="tired, muttering",
    ),
}

for name, t in clips.items():
    save(name, speak([t], VOICE))
