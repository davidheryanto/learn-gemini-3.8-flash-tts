"""Design a character voice: a serene elven archivist, in English and Japanese.

The voice is described by traits only; the lines are original.
One request per variant to stay inside the free tier's 10 TTS requests/day.

    uv run --env-file .env examples/11_character_voice.py          # en + ja
    uv run --env-file .env examples/11_character_voice.py ja
    uv run --env-file .env examples/11_character_voice.py --delete
"""

import sys

from common import client, forget_voice, load_voices, save, speak, store_voices, turn

VARIANTS = {
    "en": {
        "language_code": "en-US",
        "description": (
            "An elven archivist of indeterminate age who has kept a forest library for "
            "centuries. Her voice is soft, clear and lightly melodic, mid-pitched and calm, "
            "with a gentle, wry warmth and an unhurried, precise way of speaking."
        ),
        "lines": (
            "The old maps are wrong again. <sigh> The river moved. Rivers do that, "
            "if you give them a few centuries. <short pause> Aelindra, the lantern, please. "
            "<short pause> No, the other one. <chuckle> Thank you."
        ),
    },
    "ja": {
        "language_code": "ja-JP",
        "description": (
            "A Japanese-speaking elven archivist of indeterminate age who has kept a forest "
            "library for centuries. Soft, clear, lightly melodic voice, calm and mid-pitched, "
            "with a gentle, wry warmth and an unhurried, precise way of speaking."
        ),
        "lines": (
            "古い地図が、また間違ってる。<sigh> 川が動いたの。何百年もあれば、川は動くものよ。"
            "<short pause> アエリンドラ、ランタンを取って。<short pause> ううん、もう一つの方。"
            "<chuckle> ありがとう。"
        ),
    },
}
STYLE = "calm, gently wry"

voices = load_voices()

if "--delete" in sys.argv:
    for key in VARIANTS:
        if f"elf-archivist-{key}" in voices:
            forget_voice(voices, f"elf-archivist-{key}")
    sys.exit()

wanted = sys.argv[1:] or list(VARIANTS)
if unknown := [k for k in wanted if k not in VARIANTS]:
    sys.exit(f"unknown variant(s): {' '.join(unknown)}; choose from {' '.join(VARIANTS)}")

for key in wanted:
    v = VARIANTS[key]
    name = f"elf-archivist-{key}"
    if name not in voices:
        # No "model": Flash-Lite rejects voice design; the default creator works for both.
        created = client.voices.create(store=True, voice={
            "type": "prompted", "display_name": name,
            "gender": "female", "language_code": v["language_code"],
            "prompted": {"input": v["description"]},
        })
        voices[name] = created.id
        store_voices(voices)
        print(f"created {name}: {created.id}")
    save(f"11_elf_archivist_{key}.wav", speak([turn(v["lines"], style=STYLE)], [{"voice": voices[name]}]))
