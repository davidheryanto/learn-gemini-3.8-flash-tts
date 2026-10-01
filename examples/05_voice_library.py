"""Browse the Extended Voice Library (hundreds of voices beyond the 30 prebuilt ones).

List filters are OR within a filter and AND across filters. Your own designed or
replicated voices are listed first. Any returned `id` can be used as {"voice": id}.

    uv run --env-file .env examples/05_voice_library.py
    uv run --env-file .env examples/05_voice_library.py --lang fr-CA --search narrator
"""

import argparse

from common import client

p = argparse.ArgumentParser()
p.add_argument("--lang", nargs="*", default=["en-US", "en-GB", "en-AU"])
p.add_argument("--gender", nargs="*", help="female / male / neutral")
p.add_argument("--pitch", nargs="*", help="low / medium / high")
p.add_argument("--context", nargs="*", help="e.g. Audiobook Conversational News")
p.add_argument("--type", nargs="*", help="prebuilt / prompted / replicated")
p.add_argument("--search", help="substring match on name and description")
p.add_argument("-n", type=int, default=25)
a = p.parse_args()

filters = {
    "language_code": a.lang,
    "gender": a.gender,
    "pitch": a.pitch,
    "contexts": a.context,
    "type_": a.type,  # `type_` in Python, `type` in REST
    "search": a.search,
}
response = client.voices.list(page_size=a.n, **{k: v for k, v in filters.items() if v})

for v in response.voices or []:
    print(f"{v.id:<28} {v.display_name} ({v.language_code}, {v.accent}, {v.gender}, "
          f"pitch={v.pitch}): {v.description}")
