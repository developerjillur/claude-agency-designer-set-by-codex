# Retention: what platforms measure and how scripts hold attention

Evidence: `research/R1-youtube-longform.md` §1 and §4, `R2-shortform-and-ads.md` §1 and §5, `V2` to `V6` (measured
reference values), `R3-storytelling.md` §6.1.

## 1. What the platforms measure

- **YouTube** (R1 §1): clicks, watch time, satisfaction surveys (1 to 5 stars behind "valued watch time"), shares,
  likes and dislikes. The retention report's **Intro** is the share still watching at 0:30; spikes mark rewatches,
  dips mark skips; YouTube's own advice for a weak intro is to align the title and thumbnail with the video and rework
  the first 30 seconds. High CTR with low average view duration and falling impressions is its clickbait pattern.
  There are no official retention benchmarks: judge against the channel's own typical retention for similar length.
- **YouTube Shorts** (R2 §1.3): a view counts every start or replay since 2025-03-31; engaged views still decide
  monetization; read "viewed vs swiped away" in Studio. Shorts run up to 3 minutes.
- **Reels** (Meta Transparency Center, R2 §1.2): ranking predicts whether a viewer skips in the first seconds, watches
  nearly to the end, likes, comments, reshares, uses the audio and follows. Accounts that mostly repost others' work
  stop being recommended to non-followers (from 2026-04-30).
- **TikTok** (R2 §1.1): hook, body, close; the content proposition in the first 3 s; 90 % of ad recall impact lands
  within 6 s (TikTok's 2020 analysis).
- **Ads** (R2 §1.5): hook rate = 3-second plays / impressions (20 to 40 % is called solid); hold rate = ThruPlays /
  3-second plays. Hook rate is a diagnostic, not the goal: in Billo's 2026 data the category with the best hook rate
  ranked 12th of 14 on ROAS.

Never predict retention, CTR or conversion from a script. The panel's numbers are labelled synthetic and directional
(R10).

## 2. The architecture (long-form)

| Tool | Rule | Source |
|---|---|---|
| Confirm | say or show what was clicked within about 10 s, then escalate beyond it | R1 §3 |
| Loops | a ledger; small loops close fast, the title's question runs to the end | R1 §4, R3 R4 |
| Re-hooks | every section opens with a reason to stay (a new problem, a raised stake, "that fixes X, but it breaks Y") and a one-line signpost | R1 §4, §9.1 |
| Big re-engagements | near 3:00 and 6:00 in MrBeast's notes; for videos over 8 minutes, one at least every 3 to 4 minutes | R1 §2.1, §9.1 |
| Midpoint | a turn at 40 to 55 % against the mid-video sag (reversal, new question or the strongest counter-argument) | R1 §4 |
| Pattern interrupts | a change of mode, not noise: location, graphic, archive clip, test, a person on camera, music or pace | R1 §4 |
| Turn density | a but or therefore every 30 to 60 s; a new visual idea every 1 to 3 sentences (working targets) | R1 §4 |
| Payoff timing | confirm early, pay small debts often, pay the main debt late, then stop; never spend the best reveal in minute one | R1 §4 |
| Ending | never announce it; end fast after the payoff | R1 §2.1 |
| Chapters | titles as mini-promises; tutorials benefit most | R1 §4 |
| CTA | none before the intro pays off; tied to the next promise, in the last 5 to 20 s | R1 §4 |
| Sponsor | woven into the story so skipping loses context; after the first payoff; inside an open loop | R1 §2.1, V3 SR15 |

**Attention tools** from the reference videos (V3 B): open loops, pattern breaks, escalation (only where the format
has attempts), progress markers (ordinal signposts that promise the next reward), stakes.

**Texture changes** (V4): a voice or texture change (voice-over, sync sound, a new speaker, a sound effect, a clip) at
least every 20 s in explainers and 45 s in stories; a visual tag every 40 spoken words or fewer in explainers, 60 in
stories (both reference videos cut about every 15 to 18 words). These are our starting values: calibrate them on the
channel's own retention graphs.

## 3. Reference values measured on the videos we studied

Calibration only; a script is not scored by matching them.

| Measure | Values | Source |
|---|---|---|
| Questions per spoken minute | 1.1 to 1.5 (YASH, LEVELS, ERCRT); about 1 and 1.6 (AniThing, HimanshuG); 2.7 and 3.2 (Humm, workshop style) | V2 E, V3 3.4, V5 C |
| Longest stretch with no question | 1.9 to 4.5 min, exactly where each video sagged (a sponsor, a dense list, prose plus a plug) | V2 E |
| But-type connectors per minute | 0.8 to 1.9 | V2 E |
| Direct "you" per minute | 3.5 to 8 (V2); 5.6 to 5.8 (Humm) | V2 E, V5 C |
| Mean words per sentence | 15 to 19 (Hindi, V2); 10.9 to 12.3 (Humm, English) | V2 E, V5 C |
| Sentence length variation (sd / mean) | 0.54 to 1.01 across 14 reference transcripts; no 12-sentence stretch under 0.25 | our measurement |
| Speech rate | Hindi 190 to 240 (V2), about 200 (V3), 205 to 217 (V4); Kallaway 224, Vishen 188 | V2 to V6 |
| Main payoff | 68 % (ERCRT), 92 % (YASH); the vlog saves its biggest payoff for the last 15 % | V2 E, V4 |

The lint turns the robust ones into checks: a gap of more than 60 s (long-form) or 12 s (short) with no question,
turn, new loop or section; fewer than one turn a minute; a monotone rhythm; fewer than 3 direct addresses a minute (a
note); more than 3 questions a minute (a note).

## 4. Shorts and ads

- The first frame and the first word decide: action at frame 1, speech by about 0.5 s, the promise by 3 s (R2 §8).
- Early suspense added 16 % watch time and surprise 1.7x view-through in TikTok's hook study (Lumen 2021, R2 §1.1).
- 21 to 34 s carried TikTok's largest conversion lift in its 2021 study, while a 49 s Shorts cut matched or beat a
  15 s trailer in Google's 2024 tests (R2 §4.2): length follows the idea.
- Design for sound on and sound off: Reels play sound by default, yet 80 % of 5,616 US adults said captions make them
  more likely to finish a video (R2 §4.3). Burn captions (`meta.captions`) or carry the story in on-screen text.
- Loops: a short that ends on a line running into the first one earns replays, which now count as views (R2 §3.1).

## 5. After publishing: learn from the graph

1. Lay the retention graph over the tension map (`script.json` tensions): a dip at a high-tension beat usually means
   an unclear question or a broken promise; a dip at a flat zone confirms the flat zone (R3 §6.1).
2. Map every dip and spike to its script line and write the lesson into the next brief (R1 §5.4).
3. Compare packaging tests by watch time share, not CTR (R1 §1).
4. Feed 5 to 10 past pieces with their real results into `script.py panel validate` so the panel's judgement is
   checked against the channel's own audience (Spearman 0.4 or more before its fixes count; R10 §5.2).
