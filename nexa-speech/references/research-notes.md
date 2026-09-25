# Research notes: the sourced facts behind nexa-speech

Collected 2026-09-25 from public web sources (listed at the end with their dates). No live API call was made for this
research or for the build: everything about the API below is what Google's pages and public reports say, and the
"Unverified" section lists what nobody has measured yet. [S#] marks the source.

## Models and prices

- `gemini-3.8-flash-tts` and `gemini-3.8-flash-lite-tts` became GA on 2026-09-22. The TTS guide calls
  `gemini-3.1-flash-tts-preview` a legacy preview with the two 3.8 models as its replacement; the 2.5 previews are gone
  from the guide's model table but still have prices and no shutdown date [S1, S3, S4, S5, S6].
- Prices per 1M tokens (standard): 3.8 Flash $0.50 in / $9.00 audio out until 2026-12-31, then $1.00 / $18.00; 3.8
  Flash-Lite $0.50 / $6.00, then $1.00 / $12.00; 3.1 preview $1.00 / $20.00; 2.5 Flash preview $0.50 / $10.00; 2.5
  Pro preview $1.00 / $20.00. Batch is half price on all of them; Flex (half price, 1 to 15 minutes of latency, counts
  toward the normal rate limits) is supported on 3.8 only [S3, S6, S11].
- 25 audio tokens per second of audio, so 10 minutes is 15,000 audio tokens: about $0.135 on 3.8 Flash, $0.09 on
  Flash-Lite, $0.30 on the 3.1 preview [S6].
- One public test: 78 s of speech on 3.8 Flash cost 2.74 cents and took about 20 s to make [S17]. That is about 1.5x
  the token arithmetic; hence the ledger keeps every answer's `usage`.
- Word timings with `gemini-3.5-transcribe`: $0.003 a minute of audio in plus $0.002 a minute of text out [S6].
- Artificial Analysis TTS arena, fetched 2026-09-25: 3.8 Flash TTS #2 (Elo 1265), 3.8 Flash-Lite #6 (1239), 3.1
  Flash TTS #10 (1202), Chirp 3 HD #54 (1053) [S32].
- The docs point 3.8 Flash at acting, dialogue, heavy tag use, difficult pronunciations and long-form narration with
  stable voice and room tone, and Flash-Lite at bulk and everyday single-speaker speech [S1].
- Token limits: 8,192 in and 16,384 out on the current models, which caps one request at about 655 s of audio [S3,
  S19].

## Voices

- 30 prebuilt voices with a character word each [S1]; genders from the Chirp 3 HD list, which uses the same names
  [S20]. Each model renders a name differently.
- 3.8 adds a voice library ("hundreds" in the docs, 2,000+ in the launch post), listed with `GET /v1beta/voices` and
  filters for language, region, accent, gender, pitch, persona, context, type and a free-text search; several values in
  one filter are OR, different filters AND [S1, S15].
- Voice design (3.8): `POST /v1beta/voices` with `{store: true, voice: {model, type: "prompted", display_name,
  gender, language_code, prompted: {input}}}` returns a `voice_...` id and a `sample_audio` WAV. Every call gives a
  different voice, even with the same prompt: audition 2 or 3 and keep one. Permanent traits (age, gender, timbre,
  texture, accent) go in the design prompt, the situational delivery in the style. Up to 200 stored voices per project,
  shared with replicated voices; the docs give a 1-year life, the cookbook says 7 days: read `expire_time` from the
  answer [S1, S8, S18].
- Voice replication (3.8): a 10 to 30 s clean reference and a consent recording by the same adult speaker; the API
  checks the consent transcript and the speaker, and rejects AI-made audio; `store: false` gives a client-held
  `voicekey_...` valid for 7 days; 30 consent locales including `bn-IN` but not `bn-BD`; not offered through AI Studio
  in Illinois, Texas, the EEA, the UK, Switzerland and India; replication adds C2PA credentials [S1, S9, S15, S18].
- Two speakers per request at most (prebuilt voices); more characters, or designed voices in a dialogue, are made one
  turn at a time [S1]. Multi-speaker mode has had voice swaps, dropped and added lines and truncation in production
  reports [S29, S31].

## Languages

- 3.8 detects the language by itself: Flash covers 130+ languages, Flash-Lite 100+, both including Bangla, with no
  locale codes listed [S1, S3].
- generateContent's `SpeechConfig.languageCode` lists `bn-IN`, `en-US`, `en-GB`, `en-IN`, `en-AU` but not `bn-BD`
  [S13]; the Interactions `speech_config` has a `language` field described only as "the language of the speech"
  [S12]. Cloud Gemini-TTS has `bn-BD` as GA [S19]; Chirp 3 HD has Bengali only as `bn-IN` [S20].
- `gemini-3.5-transcribe` supports `bn-BD` and `bn-IN` and follows code-switching; word timestamps up to 30 minutes a
  call; custom vocabulary cannot be combined with timestamps [S14].

## Requests and answers

- 3.8 reads `input` text strictly as a verbatim transcript; the cookbook warns that stage directions in the text are
  spoken. Delivery goes in `annotations: [{type: "speech_metadata", style}]` [S1, S18].
- `input` may be a string, a content array or a step array [S12]. The request used here (a content array with the
  text and its annotation, `response_format: {type: "audio", mime_type: "audio/l16", sample_rate: 24000}`,
  `generation_config: {speech_config: [{voice}]}`) follows [S1] and [S18].
- Without `mime_type`, 3.8's unary answer is `audio/wav` with a 44-byte RIFF header; 3.1 and earlier return headerless
  16-bit PCM. Wrapping a WAV again gives a click and wrong length fields: check the first 4 bytes for `RIFF` [S1, S2,
  S18].
- 3.1 prompt structure: a director block (`### PERFORMANCE`, optional context) and the words under `#### TRANSCRIPT`,
  with an instruction to speak only the transcript [S23, S24].
- Check the finish reason or the step status, not only the HTTP code: truncated audio can come back as HTTP 200 with
  `finishReason: OTHER` and is still billed. Finish reasons include STOP, MAX_TOKENS, SAFETY, RECITATION, LANGUAGE,
  OTHER, BLOCKLIST, PROHIBITED_CONTENT and SPII [S13, S28, S29].
- Streaming on 3.1 cuts audio off after about 60 to 70 s with `finishReason: OTHER` (acknowledged 2026-06-23, open in
  2026-09) [S28]: masters are made with unary calls.
- Temperature, top_k and top_p are ignored on Vertex Gemini-TTS [S19]; for 3.1 Live, Google staff said temperature is
  not supported and values under 0.6 stopped the audio [S27]. A `seed` field exists [S13], but users get a different
  voice each run with a fixed seed [S26] and a review says there is no seed control [S31].

## Controllability

- 3.8 honours a short style per turn and angle-bracket tags for breaths, laughs, sighs, whispers and pauses, in
  English whatever the language; capitals for emphasis; commas, `--` and `...` for hesitation. The documented workflow:
  empty style first, a short style only where needed, the same string for the same baseline [S1, S8, S18].
- Meta-instructions ("do not switch speaker identity") and permanent traits in the style increase drift on 3.8 [S1].
- On 3.1, "quiet", "flat", "no rush" and "careful" dampen the prosody; "warm and sincere", "patient and unhurried",
  "measured but present" work better; a character name that sounds like the first transcript word can be read aloud
  [S24]. Square-bracket tags are documented for 3.1 ("200+"), best where the change should happen and never two side
  by side [S22, S24].
- Cloud Gemini-TTS markup: non-speech sounds, style modifiers, spoken adjectives (to avoid) and pauses of about 250,
  500 and 1,000 ms; aligning the style, the text and the tags matters most [S19].
- No SSML on Gemini TTS; Chirp 3 HD has SSML in preview, a numeric `speaking_rate` of 0.25 to 2.0, and IPA or X-SAMPA
  custom pronunciations [S19, S20].

## Consistency, drift and artefacts

- 3.1 slows down and drifts toward a generic accent in long generations [S25]; 3.1 Live loses volume and quality after
  about a minute [S27]; about 1 in 10 generations had a different voice on 2.5 and 3.1 [S26, S31].
- Static noise at the very end of clips on 2.5 and 3.1 was reported 2026-09-20; Google asked for a retest on 3.8 [S30].
- A "metallic" timbre on 2.5 is tied to its 2025-12 update [S31].
- Some safety blocks show up as `OTHER` rather than `SAFETY` [S29].

## Timing and captions

- Gemini TTS returns no timestamps; the chunk timeline gives sentence times for free, and `gemini-3.5-transcribe` gives
  word timestamps (`transcription_config.mode: {type: "verbatim", timestamp_granularities: ["word"]}`) [S14].
- Local aligners, for reference: WhisperX 3.8.6 has no default Bengali alignment model; the Montreal Forced Aligner
  3.4.2 has no Bengali acoustic model; ctc-forced-aligner's default model is CC-BY-NC 4.0, not usable for client work
  [S38, S39].
- Caption conventions used (common practice, not checked against a style guide in this research): at most 42
  characters a line, 2 lines, 1 to 7 s a cue, about 17 to 20 characters a second, breaks at punctuation; graphemes for
  Bangla.

## Loudness

- -14 LUFS is the level community measurements find on YouTube, Reels and TikTok; it is not an official figure [S40].
  A voice-over stem at -16 LUFS lands the mix near -14 after the music bed.
- The processing values (high-pass, 250 Hz cut, ratio-2 compressor) are gentle starting points, not sourced settings.

## Policy

- YouTube: disclosure for realistic AI-made or altered content; cloning your own voice for voice-overs needs none;
  plain AI narration is not listed either way; disclosure does not limit reach [S33]. Mass-produced repetitive content
  has not been monetizable since 2025-07-15 [S34].
- Meta: the AI label is required for realistic-sounding audio that was digitally created or altered [S35].
- TikTok: a label for AI content showing realistic people or scenes, including AI audio imitating a real person;
  generic TTS narration needs none [S36].
- Google's Generative AI Prohibited Use Policy: no impersonation to deceive, no claiming generated content is solely
  human-made to deceive [S37].
- Free-tier content may be used to improve Google's products; paid-tier content is not [S6].

## Checked on the live API (2026-09-25)

- The 3.8 answer: `steps[].content[]` audio blocks with `data`, `mime_type` (`audio/l16; rate=24000; channels=1`),
  `sample_rate` and `channels`; raw PCM; `status: completed`; no finish reason anywhere; no `id` with
  `store: false`; `usage.total_output_tokens` at 32 a second of audio (77 for 2.4 s, 214 for 6.7 s).
- The transcription answer: one text block with `word_info` annotations (`start_offset` and `end_offset` such as
  `"3s"` and `"0.100s"`, 0.1 s steps; `start_index` and `end_index` are UTF-8 byte offsets); audio in at 25
  tokens a second, no output tokens. With `language_codes: ["bn-BD"]` it split আসসালামু আলাইকুম into two words;
  without codes it joined them. Both wrote 10 and 500 for spoken দশ and পাঁচশো.
- 3.8 Flash's pace: Iapetus (English) and Sadaltager (Bangla) spoke 2 to 39 % faster than the presets' words per
  minute suggest (voiced time), every word present.

## Unverified (test on the first real run)

- Whether `speech_config[].language` accepts `bn-BD`, and whether voice design accepts `language_code: "bn-BD"`
  (fall back to `bn-IN` if not); the `gender` value format; the design answer (`id`, `expire_time`, `sample_audio`)
  and which life a designed voice really has (1 year or 7 days).
- The voice library's query parameter and field names.
- Whether 3.8 honours `speech_metadata` in batch, and whether batch and interactive sound the same (this tool renders
  interactively only).
- Whether TTS answers can carry their own word timings; whether chaining requests improves continuity; whether a seed
  gives any repeatability on 3.8; the 3.8 rate limits per project.
- Bangla with English words in Latin script, against all-Bengali and Romanized input: needs a native listen and a CER
  check.
- The Bangla number words beyond the 0 to 99 table given in the spec (hundreds, years, ordinals, times) and the
  table itself need a native reader's check before client use.

## Sources (fetched 2026-09-25 unless noted)

- [S1] Gemini API, text-to-speech (Interactions): https://ai.google.dev/gemini-api/docs/speech-generation (updated 2026-09-24)
- [S2] Gemini API, TTS for generateContent: https://ai.google.dev/gemini-api/docs/generate-content/speech-generation (updated 2026-09-24)
- [S3] Model cards: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-tts, gemini-3.8-flash-lite-tts, gemini-3.1-flash-tts-preview (page updated 2026-09-24)
- [S4] Gemini API changelog: https://ai.google.dev/gemini-api/docs/changelog (2025-05-20 to 2026-09-22)
- [S5] Gemini API deprecations: https://ai.google.dev/gemini-api/docs/deprecations (updated 2026-09-24)
- [S6] Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing (updated 2026-09-24)
- [S7] Gemini API rate limits: https://ai.google.dev/gemini-api/docs/rate-limits (updated 2026-09-02)
- [S8] Voice design: https://ai.google.dev/gemini-api/docs/voice-design (updated 2026-09-24)
- [S9] Voice replication: https://ai.google.dev/gemini-api/docs/voice-replication (updated 2026-09-24)
- [S10] Batch API: https://ai.google.dev/gemini-api/docs/batch-api (updated 2026-09-17)
- [S11] Flex inference: https://ai.google.dev/gemini-api/docs/flex-inference (updated 2026-09-23)
- [S12] Interactions API reference: https://ai.google.dev/api/interactions-api; breaking changes: https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026 (updated 2026-09-04)
- [S13] generateContent API reference: https://ai.google.dev/api/generate-content
- [S14] Audio transcription: https://ai.google.dev/gemini-api/docs/transcribe (updated 2026-09-23)
- [S15] Google blog, Gemini 3.8 Flash TTS and Flash-Lite TTS: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/ (2026-09-23)
- [S17] Simon Willison, Gemini 3.8 TTS Playground: https://simonwillison.net/2026/Sep/23/gemini-tts-playground/ (2026-09-23)
- [S18] Gemini cookbook, Get_started_TTS.ipynb and Get_Started_Voices.ipynb: https://github.com/google-gemini/cookbook (main branch)
- [S19] Cloud Text-to-Speech, Gemini-TTS: https://docs.cloud.google.com/text-to-speech/docs/gemini-tts (updated 2026-09-18)
- [S20] Cloud Text-to-Speech, Chirp 3 HD: https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd (updated 2026-09-18)
- [S22] Google Cloud blog, Gemini 3.1 Flash TTS on Google Cloud: https://cloud.google.com/blog/products/ai-machine-learning/gemini-3-1-flash-tts-on-google-cloud (2026-04-16)
- [S23] How to prompt Gemini 3.1's text to speech model: https://dev.to/googleai/how-to-prompt-gemini-31s-new-text-to-speech-model-24bb (2026-04-15)
- [S24] LiveKit, a practical guide to prompting Gemini 3.1 Flash TTS: https://livekit.com/blog/gemini-3.1-flash-tts-prompting-guide (2026-04-27)
- [S25] Forum, 3.1 Flash TTS in production: https://discuss.ai.google.dev/t/gemini-tts-gemini-3-1-flash-tts-in-production-voice-consistency-across-runs-long-input-cutoffs-accent-drift-emotional-range-guidance-roadmap/182191 (2026-09)
- [S26] Forum, keeping voices consistent between runs: https://discuss.ai.google.dev/t/how-to-keep-audio-tts-voices-consistent-between-runs/179424 (2026-08-24)
- [S27] Forum, 3.1 Flash Live voice and volume after a minute: https://discuss.ai.google.dev/t/gemini-3-1-flash-live-voice-slowly-changing-massive-audio-quality-volume-dropping-on-tts-requests-longer-than-1-minute/142499 (2026-04-27 to 2026-08-05)
- [S28] Forum, 3.1 streaming truncation past 60 s: https://discuss.ai.google.dev/t/gemini-3-1-flash-tts-preview-streamgeneratecontent-truncates-audio-finishreason-other-past-60s-while-generatecontent-non-streaming-works/169063 (2026-06-02, acknowledged 2026-06-23)
- [S29] Forum, multi-speaker bugs in production: https://discuss.ai.google.dev/t/gemini-tts-multi-speaker-mode-7-critical-bugs-after-3-weeks-in-production-finishreason-other-truncation-voice-swapping-hallucinated-lines/132776 (2026-03-15)
- [S30] Forum, static noise at the end of clips: https://discuss.ai.google.dev/t/static-noise-artifact-at-the-end-of-tts-generation-gemini-2-5-flash-preview-tts-2-5-pro-and-3-1-flash/183814 (2026-09-20)
- [S31] TTSAudit, Gemini 2.5 Pro TTS quality issues: https://ttsaudit.com/blog/google-cloud-tts-quality-issues (2026-03-07)
- [S32] Artificial Analysis TTS leaderboard: https://artificialanalysis.ai/text-to-speech/leaderboard (fetched 2026-09-25)
- [S33] YouTube Help, disclosing altered or synthetic content: https://support.google.com/youtube/answer/14328491 (fetched 2026-09-25)
- [S34] YouTube Partner Program "inauthentic content" update, effective 2025-07-15 (secondary coverage, 2025-07)
- [S35] Meta, labeling AI-generated content: https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/ (2024-02-06, updated 2025-04-01)
- [S36] TikTok Community Guidelines, Integrity and Authenticity: https://www.tiktok.com/community-guidelines/en/integrity-authenticity (2026 second-half edition)
- [S37] Google Generative AI Prohibited Use Policy: https://policies.google.com/terms/generative-ai/use-policy (2024-12-17)
- [S38] Tool status on PyPI and GitHub (fetched 2026-09-25): whisperx 3.8.6, montreal-forced-aligner 3.4.2, ctc-forced-aligner 1.0.2, stable-ts 2.19.1
- [S39] McAuliffe et al., Montreal Forced Aligner and the state of speech-to-text alignment in 2026, arXiv 2606.18466 (2026-06-16)
- [S40] Platform loudness targets, community measurements: https://clickyapps.com/creator/video/guides/lufs-targets-2025 (2025), https://www.criticallisteninglab.com/en/learn/loudness/social-media
