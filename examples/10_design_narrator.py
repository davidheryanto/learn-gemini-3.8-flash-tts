"""Iterate on a voice: render one script with several candidate voices, then listen.

Target: the soft-spoken British "product design film" narrator. The voice is
described by its traits (we don't name or clone a real person); permanent traits
go in the voice description, delivery goes in `style`, and pauses are inline tags.

    uv run --env-file .env examples/10_design_narrator.py          # all candidates
    uv run --env-file .env examples/10_design_narrator.py d2 lib1  # just these
    uv run --env-file .env examples/10_design_narrator.py --delete # remove designed voices
"""

import sys

from common import client, forget_voice, load_voices, save, speak, store_voices, turn

# Permanent traits only: age, accent, timbre, texture, baseline manner.
DESIGNED = {
    "d1": "A softly spoken Englishman in his late 50s from North-East London, with a gentle, "
          "slightly breathy mid-range voice. He speaks slowly and earnestly, almost hushed, "
          "with quiet reverence for the objects he describes.",
    "d2": "A thoughtful British industrial designer in his 50s with a soft Essex-London accent "
          "and a light, airy, intimate voice close to the microphone. Unhurried and sincere, "
          "he lingers on certain words as if savouring them.",
    "d3": "A calm, introspective English narrator in his 50s with a soft London accent and a "
          "warm, breathy, understated voice. He sounds modest, precise and deeply sincere, "
          "speaking in measured phrases with long thoughtful pauses.",
}
# Closest Extended Voice Library matches (see 05_voice_library.py).
LIBRARY = {
    "lib1": "en-gb-storyteller-4",  # 56, deep, velvety, unhurried
    "lib2": "en-gb-podcaster-1",    # intimate talkshow
    "lib3": "en-gb-csagent-12",     # light, airy, precise
}

STYLE = "hushed, slow and sincere, with reverence"
SCRIPT = [
    "We believe that... <short pause> a product should feel inevitable.",
    "Not designed, <short pause> but somehow... discovered.",
    "Every curve, <breath> every edge, has been considered. <long pause> "
    "And when you hold it, <short pause> it simply... disappears.",
]

voices = load_voices()

if "--delete" in sys.argv:
    for key in DESIGNED:
        if f"narrator-{key}" in voices:
            forget_voice(voices, f"narrator-{key}")
    sys.exit()

wanted = sys.argv[1:] or [*DESIGNED, *LIBRARY]
if unknown := [k for k in wanted if k not in DESIGNED and k not in LIBRARY]:
    sys.exit(f"unknown candidate(s): {' '.join(unknown)}; choose from {' '.join([*DESIGNED, *LIBRARY])}")

for key in wanted:
    if key in DESIGNED:
        name = f"narrator-{key}"
        if name not in voices:
            v = client.voices.create(store=True, voice={
                "type": "prompted", "display_name": name,
                "gender": "male", "language_code": "en-GB",
                "prompted": {"input": DESIGNED[key]},
            })
            voices[name] = v.id
            store_voices(voices)
            print(f"created {name}: {v.id}")
        voice = voices[name]
    else:
        voice = LIBRARY[key]

    # One request per candidate: the free tier allows only 10 TTS requests/day.
    text = " <long pause> ".join(SCRIPT)
    save(f"10_{key}.wav", speak([turn(text, style=STYLE)], [{"voice": voice}]))
