"""Two-speaker dialogue in a single request, with |backchannels|.

- Up to 2 speakers per request, prebuilt voices only (for custom voices see 07).
- speech_config becomes an OBJECT: {"speakers": [...]}.
- Every turn must carry `speaker` matching one of the configured speakers.
- |pipes| inside a turn are the *other* speaker's reactions or overlapping speech.

    uv run --env-file .env examples/03_two_speakers.py
"""

from common import save, speak, turn

speech_config = {
    "speakers": [
        {"speaker": "Maya", "voice": "Aoede"},
        {"speaker": "Sam", "voice": "Puck"},
    ],
}

script = [
    turn("So the launch is Thursday |oh hmm| Are we actually ready?", speaker="Maya"),
    turn("Ready enough |oh really?| The last blocker cleared this morning.", speaker="Sam",
         style="casual, a little smug"),
    turn("Then let's ship it |absolutely| and watch the dashboards. <laugh>", speaker="Maya"),
    turn("Okay, on three |ok| ready? one. two. three. |ship| ship |it| it!", speaker="Sam",
         style="excited"),
]

save("03_dialogue.wav", speak(script, speech_config))
