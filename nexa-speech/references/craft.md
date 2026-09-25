# Craft: scripts, styles, tags, pronunciation, drift and platform rules

What makes Gemini text-to-speech sound like one person reading well, and what breaks it. The sources, with dates, are
in `research-notes.md`; "unverified" marks what nobody has measured yet.

## 1. Write for the ear

The listener cannot see the page. What is not said is not there.

- Short sentences, one idea each. Put the word that matters at the end of the sentence, where the stress falls.
- Name the subject: "The river carries silt", not "It carries silt" after a heading the listener never heard.
- No labels, captions or screen references read out: not "Chapter 3", "Figure A", "see below", "this list",
  "নিচে দেখুন". `plan` warns about the common ones.
- Numbers, dates and money can stay as digits in the script: the tool writes them out (English, or Bangla words with
  lakh and crore) and keeps the digits for the captions. Avoid long lists of numbers in a row; a listener keeps two.
- English: contractions where a person would use them. Natural disfluencies only where the format allows (a vlog, a
  character), never in an ad or a tutorial.
- Keep the three levers aligned: the style, the meaning of the words and the tags. A sad line with a cheerful style
  sounds wrong; emotionally matching text is far more reliable than neutral text with a strong style.
- Short lines that must stand alone ("Ready?") get no style and two takes: rich direction distorts short
  utterances.
- Write the script first and lock it, then render. The cache key is the spoken text: a changed sentence is a new
  paid call, and the old take stays in the cache.

## 2. Styles: short, fixed, and in the right place

On 3.8 the style goes in `speech_metadata.style`, never in the text: 3.8 reads the text word for word, so a direction
written in it is spoken. On 3.1 and 2.5 it goes in `### PERFORMANCE` above `#### TRANSCRIPT`.

- **Short and byte-identical.** One phrase, the same string in every chunk. The docs for 3.8 say long "audio
  profile" and "director's notes" blocks are the most common cause of voice drift.
- **Workflow from the docs:** try an empty style first; add a short style only where a line needs it; reuse the exact
  string for the same baseline. Delivery changes go in the profile's `modes`, one short style each.
- **Documented on 3.8:** "speaking slowly", "speaking rapidly", "whispering", "out of breath", "muttering",
  "sarcastic", "monotone and flat", "high pitch, cheerful and excited inflection". Finer steps ("a little faster") are
  unverified.
- **Words that work** (a 3.1 review): "warm and sincere", "patient and unhurried", "measured but present".
- **Words that flatten** (the same review, on 3.1): "quiet", "flat", "no rush", "careful".
- **Never in a style:** meta-instructions such as "do not switch speaker identity" or "maintain identical timbre"
  (they increase drift on 3.8), and permanent traits such as age, gender, a name or a fixed accent (on 3.8 those
  belong in voice design).
- **Pick a voice whose base character fits the job:** a breathy voice (Enceladus) helps "tired", an upbeat one
  (Puck) helps "excited".

## 3. Tags

3.8 inline tags, in English even when the text is Bangla, human sounds only:

- breaths and sounds: `<breath>`, `<heavy breath>`, `<exhales>`, `<sigh>`, `<sighs>`, `<laugh>`, `<laughter>`,
  `<chuckle>`, `<chuckles>`, `<giggle>`, `<gasp>`, `<cough>`, `<throat-clearing>`, `<tsk>`, `<phew>`, `<pff>`,
  `<yawn>`, `<sob>`, `<cry>`, `<whimper>`;
- louder: `<shout>`, `<scream>`, `<shriek>`, `<groan>`, `<growl>`, `<grunt>`, `<hiss>`, `<moan>`, `<pant>`,
  `<snort>`, `<snicker>`, `<sneeze>`, `<cheer>`, `<cackle>`, `<argh>`, `<grr>`;
- `<whispers>`, `<whispering>`; pauses: `<short pause>`, `<long pause>`.

A profile allows only what is in its `tags_allowed` (by default `<short pause>`, `<long pause>`, `<breath>`): add a
tag there when a script needs it. Emphasis on 3.8: write the stressed word in capitals ("a VERY important point").
Hesitation: commas, `--` and `...`.

On 3.1 and 2.5 the tool turns `<tag>` into `[tag]`. Google's 3.1 material shows `[whispers]`, `[laughs]`, `[sighs]`,
`[excitedly]`, `[sarcastically]`; the documented ones sound fuller than invented ones, and two tags should never sit
side by side. On Cloud Gemini-TTS, adjective tags such as `[scared]` are spoken as words: use the style instead.

Square brackets on 3.8 are not a direction mechanism; `plan` warns about them.

## 4. Pace and pauses

- There is no numeric speaking rate on any Gemini TTS model; pace comes from the style ("speaking slowly").
- Pauses inside a chunk: punctuation, `<short pause>`, `<long pause>`.
- Pauses between sentences, paragraphs and scenes: never ask the model. The tool lays exact silences (the profile's
  `gaps_ms`, `@pause`) over one room tone, so the timing is fixed and editable. Rules of thumb: sentence 250 to 400
  ms, paragraph 600 to 900 ms, scene change 900 to 1,500 ms or covered by music.
- Starting paces (rules of thumb until three chunks calibrate the voice): English documentary 135 to 150 words a
  minute, explainer 150 to 165, ad 160 to 185; Bangla about 125 to 135 (the pace of an earlier production pipeline).
- To fit a scene, `fit` changes the gaps first, then stretches by at most 6% (10% for ads). Past about 8 to 10% a
  stretch is audible: re-render with a pace style or cut words instead.

## 5. Pronunciation (Gemini has no phoneme or lexicon API)

1. **Two texts per chunk.** Captions show `display`, the voice says `spoken`; the lexicon and `{display|spoken}`
   pairs make the difference, and the cache key hashes the spoken text.
2. **Numbers, dates, money and units** as words (the tool does it). Bangla: always Bangla words, never digits.
3. **Acronyms:** letters said one by one are written out ("A I", in Bangla "এআই"); acronyms said as words stay as they
   are ("NASA").
4. **Names and brands:** spell them as they sound, hyphenated at syllables ("Nexa-Lance"), and keep the spelling in the
   lexicon so every chunk says it the same way.
5. **Bengali words inside English narration:** try a Latin respelling and Bengali script, and keep the better one;
   mixed scripts may switch the accent (unverified).
6. **Check every name:** `qa --asr` fails a chunk when a lexicon term is not heard.
7. **When dozens of exact pronunciations matter** (a software tutorial, pharma), Cloud Chirp 3 HD takes IPA or X-SAMPA
   pronunciations and SSML `<phoneme>`, at the cost of plainer delivery.

## 6. Bangla and Banglish

- Gemini 3.8 detects the language by itself; the API's locale lists name `bn-IN` but not `bn-BD` for generateContent,
  so the tool sends no language code unless a profile asks for it. The accent comes from the voice (design one with a
  Dhaka description on 3.8) and, on 3.1, from one line in the performance block.
- Write Bangla in Bengali script. Keep English words in Latin script only where the audience says them as English
  (brand and app names, "video editing"); `plan` knows a short list of such words and warns about the rest.
- Never send Romanized Bangla ("ami tomake bhalobashi"): it will likely be read with an English or Hindi accent.
  Convert it to Bengali script first.
- Check the result with a native listener and `qa --asr` (character error rate). Code-switched lines are transcribed
  without a language code so the recogniser can follow both languages.
- Grade letters and abbreviations go to Bangla words; `খ্রি.` and `হি.` are said in full by the tool.

## 7. One voice across fifty chunks

1. One model id per project; never fall back mid-project (a fallback means re-rendering every chunk).
2. One voice: a prebuilt name, or a designed id with its `expire_time`. Keep the design sample; a lost designed voice
   cannot be designed again (the same prompt gives a new voice).
3. One style string, byte-identical, and named modes for changes.
4. Chunks at sentence or paragraph boundaries, of similar length (pace drifts with length; 3.1 slows and drifts toward
   a generic accent in long generations).
5. One transport for the whole project: nobody has shown that batch and interactive read a prompt the same way.
6. No context text on 3.8 (it would be spoken). Seeds give no repeatability in public reports; temperature is never
   set.
7. Best of N for hooks, calls to action and emotional peaks (`@takes 3`), and one automatic re-roll for a failing
   chunk, all in the ledger.
8. Post-level consistency: every chunk gain-matched to the median, one room tone, fixed pauses, one final loudness
   step.

### Artefacts seen in 2026 and what the tool does

| Artefact | Seen on | Detected by | Fix |
|---|---|---|---|
| audio cut off mid-sentence, HTTP 200, finish reason OTHER, still billed | 2.5 multi-speaker; 3.1 streaming past 60 to 70 s; about 1 in 100 long calls | gate 1, gate 2, gate 4 | unary calls, chunks of 45 s or less, one re-roll |
| a different voice between runs with the same settings | 3.1 and 2.5 | listening (speaker similarity is not measured) | 3.8 with a stored voice, a short fixed style, best of N |
| pace slows and the accent drifts inside a long generation | 3.1 | gate 5 (rate) | shorter chunks |
| volume and quality drop after about a minute | 3.1 Live | gate 5 (loudness) | chunks under 60 s, gain matching |
| voices swapped, lines added, skipped or doubled | multi-speaker 2.5 and 3.1 | gate 4 | one request per turn (the tool never sends two speakers at once) |
| directions read aloud | 3.1 without a delimiter; 3.8 with directions in the text | gate 4 (direction words heard) | style in `speech_metadata`; the `#### TRANSCRIPT` delimiter |
| static or noise after the last word | 2.5 and 3.1 (reported 2026-09-20) | gate 3 | trimmed to the last word plus 150 ms, 40 ms fade, room tone |
| clipped first sound or a click | general; a WAV wrapped twice | gate 3, gate 1 | trimmed, 8 ms fade-in, the RIFF check |
| thin, ringing timbre | 2.5 after its 2025-12 update | gate 5 (spectral centroid) | re-roll, or another model |
| names, acronyms or numbers said wrong | all | gate 4 (lexicon terms) | the lexicon, numbers as words |
| safety or "copyrighted works" refusals, not deterministic, can depend on the voice | 3.1 (also in an earlier production pipeline); 2.5 can show them as OTHER | the finish reason, the error text | report it; shorten or rephrase; try the other voice once; never loop |

Long verbatim runs of published text (scripture, translations, lyrics) can be refused as resembling copyrighted
works: keep such runs short.

## 8. Post-processing, gently

Gemini output already sounds processed: less is better. The chain is a high-pass at 70 Hz, a 1.5 dB cut at 250 Hz, a
compressor at ratio 2 and one loudness step; these are gentle starting points, not sourced settings. The source is 24
kHz, so nothing above about 12 kHz exists: upsampling to 48 kHz adds none, and "exciter" tricks need a listening test
first. Keep the 24 kHz masters forever and hand the editor the 48 kHz, 24-bit file. Encode lossy formats only at
delivery, at a generous rate: in an earlier production pipeline, Opus at 32k in `voip` mode cut 4 to 8 kHz by 2.4 dB
(dulling sibilants and Bangla conjuncts), and 96k with `-application audio` did not.

The voice-over stem sits at -16 LUFS integrated and -1.5 dBTP, so the final mix lands near -14 LUFS after the music
bed; -14 LUFS is the level community measurements find on YouTube, Reels and TikTok (not an official figure).

## 9. Platform labels and voice consent

- **YouTube** (Help page, fetched 2026-09-25): disclose realistic AI-made or altered content; the examples include
  making a real person seem to say what they did not. Cloning your own voice for voice-overs or dubs needs no
  disclosure. Plain AI narration is not listed either way: tick "altered or synthetic" when the voice could be taken
  for a real person speaking (a presenter, a testimonial, a character presented as real), and always for a clone of
  anyone but yourself. Disclosure does not limit reach. Mass-produced, repetitive content (templated slideshows with AI
  narration) has not been monetizable since 2025-07-15.
- **Facebook and Instagram** (Meta, 2024-02-06, updated 2025-04-01): use the AI label for realistic-sounding audio that
  was digitally created or altered.
- **TikTok** (Community Guidelines, second half of 2026): label AI content that shows realistic people or scenes,
  including AI audio that imitates a real person; generic TTS narration that is not a recognisable voice needs no
  label. Misleading AI content on matters of public importance is not allowed.
- **Google's Generative AI Prohibited Use Policy** (2024-12-17): no impersonating a person to deceive, no claiming
  generated content was made by a human to deceive.
- **Voice replication** (3.8; not offered by this tool): the owner records a fixed consent statement and the API checks
  that the same adult speaker says it; AI-made reference or consent audio is rejected; there are 30 consent locales
  (`bn-IN` among them, not `bn-BD`); replication through AI Studio is not offered in Illinois, Texas, the EEA, the UK,
  Switzerland and India, and it adds C2PA credentials. For client work, also get written permission, keep the consent
  audio private, and never replicate a public figure.
- Every Gemini audio clip carries a SynthID watermark. Never present a synthetic voice as a real customer, expert or
  presenter.
