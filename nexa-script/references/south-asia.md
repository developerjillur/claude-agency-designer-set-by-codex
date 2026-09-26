# Scripts for Bangladesh and India (Bangla, Banglish, Hindi)

The audience comes from the brief, never from the writer's defaults: a Bangladeshi brand gets Bangladeshi places,
prices and moments; an Indian channel gets Indian ones; a global brand gets its own market. Evidence: the South Asian
sections of `research/V2-script-and-story-part1.md` §G, `V3-story-part2.md` §3.6, `V4-story-part3.md` (SA 1 to 15),
`V5-humm-storytelling.md` §E, `V6-kallaway-vishen.md` (Bangla word lists), and natural-text's `references/bangla.md`.

## 1. Register and address

- Everyday চলিত Bangla with the English words people really say (hook, video, subscribe, research); no সাধু forms,
  no bookish shuddh wording, no Kolkata words in a Bangladeshi script. natural-text sets the words; `lint --voice`
  runs its checks.
- One address form through the narration: আপনি for broad, client and mixed-age work; তুমি for a young niche that
  talks that way; তুই only inside character dialogue (V4 SA 2; the lint flags a mix outside quotes).
- Kinship terms make strangers warm when used the way people really do: ভাই, আপা, আন্টি, খালা, মামা, চাচা (V4 SA 3).
- Bangla connectors, never Hindi ones: কিন্তু, তবে, আসলে, বরং, অথচ, তাই, ফলে (V3 SL18; the lint fails Devanagari in a
  Bangla script and flags "lekin", "matlab" in Banglish).
- Hindi scripts for India: everyday Hinglish, English technical words inside the Hindi; keep one of tum or aap (V4 SA 2).

## 2. Numbers, money, places

- Lakh and crore in narration; taka (৳) for Bangladesh, rupees for India; Bangla numerals in Bangla on-screen text;
  convert dollars and set them against a local scale (V4 SA 8, V3 SR12).
- Local routes and places in the stakes: Teknaf to Tetulia as the end-to-end journey in Bangladesh; a bank queue, a
  bus counter, a cousin's wedding for a Bangladeshi brand (V3 3.6, V5 E).
- Superlatives ("the longest train", "the biggest market") need a fact check and an "as of" date (V4 SA 14).

## 3. What lands

- Shared memories: Eid journeys home by train, bus and launch; tea stalls; station food; exam pressure; the small-town
  to big-city jump; the government-job and BCS dream in the role the corporate job plays in Indian scripts (V2 G3,
  V4 SA 4).
- Food as social glue: strangers sharing home-made food on a journey (V4 SA 5); fuchka, chotpoti and the tea stall in
  Bangladesh, chaat in India.
- Family and money stakes (medicine bills, loan EMIs, what relatives will say) land hard; never mock the audience for
  them (V2 G3, G8).
- Comedy and an audience surrogate (a sidekick voicing the viewer's doubts) keep explainers moving (V3 3.6).
- Frugal-production transparency (one person, one phone, the real cost) makes a strong tease for creator audiences
  (V4 SA 12).
- Multilingual moments feel real: keep them and subtitle the key lines; regional dialects can play that role in
  Bangladesh (V4 SA 13).

## 4. What to avoid

- Crude jokes, slurs, sexual jokes, and jokes about another region's language (V3 3.6).
- India against Bangladesh comparisons as hooks: they draw heated comments (V4 SA 10).
- "Your teachers or parents were wrong" breaks as a default; prefer "what we were taught is incomplete", pay it off
  with evidence, and never break a religious belief (V4 SA 7).
- Naming cricketers without checking current feeling: some Bangladeshi players became politically charged after 2024
  (V2 G4).
- Borrowed film, TV and creator clips in client work: use original footage, licensed stock or generated visuals
  (V2 G7, V4 SA 10).
- Money hooks that imply guaranteed returns; false scarcity in mid-roll promos (V4 SA 9, 11).
- Filming women and children without consent; unblurred minors; disrespect to elders, faith, gender or service
  workers (V4 SA 6).

## 5. Platforms and greetings

- Bangladesh is Facebook first, then YouTube and TikTok; India is YouTube and Instagram Reels (TikTok has been banned
  there since 2020) (V2 G5).
- Greetings are religion-coded (salam, namaskar): stay neutral or match the creator. When a creator always greets,
  the greeting comes right after the first hook line and lasts a second; it never opens the video (V2 G6, V4 SA 15).
- On-screen text: default to Bangla script for broad audiences, English terms in Latin script; test Banglish only
  for the audience that writes it (V3 3.6).
- Festivals and solemn days follow codex-design's `references/occasions.md`: no selling on solemn days.

## 6. Pace and voice

- Hindi creators in our references ran 173 to 252 words a minute; do not reuse Hindi figures for Bangla (V3 3.6).
- Time a Bangla script with the real TTS voice (nexa-speech) and set `meta.wpm`; the default factor (0.84 of English)
  is a placeholder until measured.
- Judge Bangla with native-reader judgement: model judges inflate scores in non-Latin scripts, and whisper-style
  transcription is not trusted for Bangla (use agy-watch-video's Gemini transcription to check a finished voice-over).

## 7. Bangla word lists the lint uses

| List | Words |
|---|---|
| Contrast (but) | কিন্তু, অথচ, তবে, আসলে, বরং, যদিও, তবুও |
| Consequence (so) | তাই, ফলে, সেজন্য, এজন্য, এর মানে, তার মানে |
| And-then | এরপর, তারপর, আরেকটা, এছাড়া, পরের, দ্বিতীয়ত |
| Greetings and preambles | আসসালামু আলাইকুম, হ্যালো বন্ধুরা, আজকের ভিডিওতে, কেমন আছেন সবাই |
| Morals | শিক্ষা হলো, মনে রাখবেন, দিনশেষে |
| Vague payoff | বাকিটা তো জানোই, বাকিটা ইতিহাস |
| Fake loops | শেষ পর্যন্ত দেখুন, শেষে একটা বোনাস, স্কিপ করবেন না |
| Hedges | হয়তো, সম্ভবত, মনে হয়, হতে পারে (except "আপনি হয়তো ভাবছেন", thought narration) |
| Named emotions (key moment) | নার্ভাস ছিলাম, খুশি হলাম, লজ্জা পেলাম, ভয় পেয়ে গেলাম, মন খারাপ হয়ে গেল |
| Reported speech | বলল যে, জানাল যে, জিজ্ঞেস করল যে |
| Thought frames | মনে মনে ভাবছি, মাথায় একটাই কথা ঘুরছে |

These are detection lists, calibrated against the natural-text Bangla pack; extend them from real scripts, not from
translation.
