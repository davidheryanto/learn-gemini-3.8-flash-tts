"""Flash vs Flash-Lite with the same request: listen and pick.

Flash: best fidelity, acting, dialects, multi-speaker, and long-form ($9/1M output tokens).
Flash-Lite: faster and cheaper ($6/1M) for volume, voice agents, and read-aloud.
These are paid-tier prices through 2026; they double on 2027-01-01.

    uv run --env-file .env examples/09_compare_models.py
"""

import time

from common import save, speak, turn

text = turn(
    "Right, so -- <chuckle> I wasn't expecting the dragon to be POLITE about it. "
    "<short pause> But here we are.",
    style="wry, amused",
)

for model in ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"]:
    t = time.perf_counter()
    audio = speak([text], [{"voice": "Fenrir"}], model=model)
    print(f"{model}: {time.perf_counter() - t:.2f}s")
    save(f"09_{model}.wav", audio)
