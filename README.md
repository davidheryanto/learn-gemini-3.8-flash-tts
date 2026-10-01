# Learn Gemini 3.8 Flash TTS

A hands-on starter for Gemini 3.8 Flash TTS and Flash-Lite TTS (launched 2026-09-23). Each script in `examples/` covers one feature. Run them in order and listen to the output in `out/`.

## Setup

```bash
cp .env.example .env          # paste your key from https://aistudio.google.com/apikey
uv run --env-file .env examples/01_hello.py
```

You can also `export GEMINI_API_KEY=...` and drop the `--env-file .env` flag. To run the examples on the cheaper model, set `TTS_MODEL=gemini-3.8-flash-lite-tts` (01 hardcodes the model to show the raw request, and 09 always runs both).

| Script | What you learn |
|---|---|
| `01_hello.py` | The full request with no helpers |
| `02_direction.py` | `style` vs inline `<tags>`, pauses, emphasis |
| `03_two_speakers.py` | Two-speaker dialogue in one request, `\|backchannels\|` |
| `04_streaming.py` | Streaming PCM, time to first audio, live playback with `aplay` |
| `05_voice_library.py` | Searching hundreds of library voices by language, gender, or context |
| `06_voice_design.py` | Creating a voice from a text description (cached and reusable) |
| `07_long_form.py` | One request per turn, then joining the audio: long scripts and custom-voice scenes |
| `08_voice_replication.py` | Cloning your own voice from a reference clip plus a consent clip |
| `09_compare_models.py` | Flash vs Flash-Lite on the same input |
| `10_design_narrator.py` | Iterating on a voice: designed and library candidates, same script, then listen |
| `11_character_voice.py` | Designing an original character voice (English and Japanese) from traits alone |

AI Studio's playground (https://aistudio.google.com/generate-speech) is the fastest way to audition voices and design new ones. Copy the `voice_...` ID it gives you into code.

## The article in 30 seconds

- **Flash TTS** is for creative work: voice design from prompts, line-by-line acting, dialects, long-form, and two-speaker scenes.
- **Flash-Lite TTS** costs less and runs faster, for dubbing, voice agents, and read-aloud. It replaces `gemini-3.1-flash-tts-preview`.
- Voices: 30 prebuilt, 2,000+ in the library, unlimited designed voices, and replicated voices (from a 30 s sample plus spoken consent).
- Both models handle hours of audio with little drift, natural two-speaker turn-taking, and vocal bursts and backchannels.
- Every output carries a SynthID watermark. The announcement's footnote says replication *through AI Studio* is unavailable in Illinois, Texas, the EEA, the UK, Switzerland, and India.

## Cheat sheet

### Models

| | `gemini-3.8-flash-tts` | `gemini-3.8-flash-lite-tts` |
|---|---|---|
| Use for | Audiobooks, drama, complex dialogue, heavy tags, dialects | Volume, voice agents, read-aloud, replication |
| Languages | 130+ (auto-detected) | 100+ |
| Output price, paid tier (2026) | $9 / 1M audio tokens (~$0.00225 per 10 s) | $6 / 1M (~$0.0015 per 10 s) |

- Input costs $0.50 / 1M text tokens on both models.
- Prices double on 2027-01-01. Batch API is half price. There is a free tier.
- Limits: 8,192 input tokens and 16,384 output tokens per request.

### Request shape (Interactions API, `google-genai >= 2.25`)

```python
interaction = client.interactions.create(
    model="gemini-3.8-flash-tts",
    input=[{"type": "user_input", "content": [
        {"type": "text", "text": "Words to speak, verbatim.",
         "annotations": [{"type": "speech_metadata", "style": "warm", "speaker": "Joe"}]},
    ]}],
    response_format={"type": "audio"},                     # + "mime_type", "sample_rate"
    generation_config={"speech_config": [{"voice": "Kore"}]},
)
audio = base64.b64decode(interaction.output_audio.data)
```

- **One speaker:** `speech_config` is a **list**: `[{"voice": "Kore"}]`.
- **Two speakers:** `speech_config` is an **object**: `{"speakers": [{"speaker": "Joe", "voice": "Puck"}, {"speaker": "Jane", "voice": "Kore"}]}`. Every turn also needs `speaker` in its metadata.
- **`voice`** accepts a prebuilt name, a library ID, a designed or replicated `voice_...` ID, or a `voicekey_...`.

### Directing the performance

`text` is read **verbatim**. A stage direction like "Say cheerfully:" gets spoken aloud, so put delivery instructions in the fields below.

| You want | Put it in | Example |
|---|---|---|
| Emotion, pace, pitch, or whispering for a whole turn | `speech_metadata.style` | `"whispered urgently"`, `"speaking slowly"`, `"monotone and flat"` |
| A sound at one exact moment | `<tag>` inline | `Wait... <short pause> did you hear that? <sigh>` |
| Stress on a word | CAPITALS | `This is a VERY important point!` |
| Hesitation | `,` `--` `...`, disfluencies | `Oh uh, yeah I think... hm` |
| The other speaker reacting mid-turn | `\|pipes\|` inline | `So the launch is Thursday \|oh hmm\| are we ready?` |
| A permanent trait (age, gender, accent) | Voice design, **not** `style` | see `06_voice_design.py` |

**Tags:** `<laugh>` `<chuckle>` `<giggle>` `<cackle>` `<snicker>` `<sigh>` `<gasp>` `<breath>` `<heavy breath>` `<exhales>` `<pant>` `<cough>` `<sneeze>` `<throat-clearing>` `<yawn>` `<cry>` `<sob>` `<whimper>` `<groan>` `<moan>` `<growl>` `<grunt>` `<grr>` `<hiss>` `<argh>` `<pff>` `<phew>` `<tsk>` `<snort>` `<scream>` `<shout>` `<shriek>` `<cheer>` `<whispers>` `<short pause>` `<long pause>`

Use English tags even when the transcript is in another language. Stick to human vocalizations; sound effects like applause don't work.

**Getting good results:**

1. Try with an empty `style` first. Most lines don't need one.
2. Add a short `style` only where a line needs it, and reuse the same short string to keep a consistent baseline.
3. Build the character once with Voice design instead of long "Director's Notes" prompts, which cause voice drift.
4. Don't add instructions like "keep the voice consistent". Extra prompt text makes drift worse.
5. For voice agents, make one TTS call per turn as the LLM's text arrives.

### Audio formats

| Call | Default | Notes |
|---|---|---|
| Unary | `audio/wav`, 24 kHz mono 16-bit, with header | Write the bytes straight to `.wav`. Don't add another header. |
| Streaming (`stream=True`) | `audio/l16`, headerless PCM | Concatenate the chunks and wrap them in a WAV header once |
| Telephony | `audio/mulaw`, `audio/alaw` | Set `response_format.mime_type`. `sample_rate` can be 24000, 16000, or 8000. |

### Voices

- **30 prebuilt voices:** Zephyr (bright), Puck (upbeat), Charon (informative), Kore (firm), Fenrir (excitable), Leda (youthful), Orus (firm), Aoede (breezy), Callirrhoe (easy-going), Autonoe (bright), Enceladus (breathy), Iapetus (clear), Umbriel (easy-going), Algieba (smooth), Despina (smooth), Erinome (clear), Algenib (gravelly), Rasalgethi (informative), Laomedeia (upbeat), Achernar (soft), Alnilam (firm), Schedar (even), Gacrux (mature), Pulcherrima (forward), Achird (friendly), Zubenelgenubi (casual), Vindemiatrix (gentle), Sadachbia (lively), Sadaltager (knowledgeable), Sulafat (warm).
- **Library:** `client.voices.list(language_code=[...], gender=[...], pitch=[...], contexts=[...], search="...")`.
- **Design:** `client.voices.create(store=True, voice={"type": "prompted", "prompted": {"input": "<1-2 sentence description>"}, ...})`. The response includes a `sample_audio` preview.
- **Replicate:** `client.voices.create(store=True, voice={"type": "replicated", "replicated": {"source_audio": ..., "consent_audio": ...}})`.
- **Manage:** `client.voices.get(id=...)` and `client.voices.delete(id=...)`.
- **Storage limits:** stored voices are capped at 200 per project and expire after 1 year. Stateless `voicekey_...` keys (`store=False`) expire after 7 days.

### Limits to remember

- **Free tier: 10 Flash TTS requests per day.** Flash-Lite has its own quota. Send one request per clip rather than one per sentence.
- **Voice design with Flash-Lite:** the docs say it's supported, but `voices.create` fails if `voice.model` is set to Lite. Leave `model` out; the resulting voice works with both models.
- **Voices belong to the project behind your API key.** `out/voices.json` caches IDs, so if you switch keys, delete it or you'll get 404 errors.

- Text in, audio out only. No tools, thinking, or Live API.
- A single request supports at most 2 speakers, and they must be prebuilt voices. For custom voices or longer scripts, make one request per turn and join the audio (`07_long_form.py`).

## Sources

- Announcement: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/
- TTS guide: https://ai.google.dev/gemini-api/docs/speech-generation
- Voice design: https://ai.google.dev/gemini-api/docs/voice-design
- Voice replication: https://ai.google.dev/gemini-api/docs/voice-replication
- Models: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-tts and https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-lite-tts
- Pricing: https://ai.google.dev/gemini-api/docs/pricing
