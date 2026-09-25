# Licence and provenance

What you may do with the music and sound nexa-sound makes, what to tell a client, and which sources the skill never
uses for client work. Plain words; the sources and their dates are at the end. This is not legal advice: when a
client's contract needs certainty, read the terms yourself.

## What to tell a client

`credits DIR --out CREDITS.txt` writes this, with the details of each track, for the delivery folder.

- You may use Lyria music in commercial videos, including client work. Google claims no ownership of it.
- It is not exclusive: Google can make similar music for others. So do not register it with Content ID, sell it as
  exclusive stock, or promise a client exclusivity.
- Pure AI music is probably not protected by copyright in the US, so a copycat may be hard to stop. Your own lyrics
  and real editing work count as human authorship.
- Every Lyria track carries Google's invisible SynthID watermark, and the original MP3s carry a C2PA credential. The
  untouched originals are kept, and nobody tries to remove either. Do not present the music as made only by people in
  order to deceive.
- Google offers no copyright indemnity for Lyria through the Gemini API. If a client needs indemnity, Google Vids
  (Workspace) is the indemnified route.
- Never ask for "in the style of" an artist or for real song lyrics: those prompts are blocked and break Google's rules.
- Sound effects come from the skill's own synthesiser or CC0 sources (no credit needed) unless a credit line is
  listed. Non-commercial (NC) sounds and non-commercial AI models are never used.
- YouTube: background AI music does not need the "altered or synthetic" label by itself. That label is for realistic
  depictions of real people, places or events.

## Lyria music, in plain words

**Ownership.** The Gemini API Additional Terms say Google won't claim ownership of the content you generate. You also
accept that Google may generate the same or similar content for others, and you are responsible for how you, and
anyone you share it with, use it.

**Data.** On a paid (billing-enabled) project, prompts and responses are not used to improve Google's products; they
are logged for a limited time to detect abuse. On the free tier they are used to improve products and people may read
them. Lyria 3.5 and Lyria 3 Clip have no free tier. Lyria RealTime (experimental, free for now) on an unpaid key falls
under the unpaid terms. nexa-sound sends `"store": false` so interactions are not kept on Google's side.

**Copyright.** The US Copyright Office (Part 2 of its AI report, 2025-01-29) says prompts alone do not give enough
control for human authorship: purely generated music is probably not protected. Lyrics a person wrote, and human
creative arrangement or editing, can be.

**Indemnity.** Google Cloud's list of indemnified generative AI services (last modified 2026-07-20) does not include
Lyria or the Gemini Developer API. It does include Google Vids in Workspace, which can make Lyria tracks.

**SynthID and C2PA.** Google embeds SynthID, an inaudible watermark, in all Lyria audio. nexa-sound never tries to
remove, mask or test the removal of it, and neither should you: Google's Prohibited Use Policy bans circumventing its
protections. Lyria MP3s from the API start with a C2PA manifest (seen in Google's sample output). Any edit drops it,
and it would no longer match the edited audio anyway, so the untouched original is kept next to every edit, read-only,
with a sidecar that records the model, the prompt, the date and the file's SHA-256.

**Artists, songs and lyrics.** Prompts that ask for an artist's voice or copyrighted lyrics are blocked by Google, and
naming artists is against the spirit of the terms. `brief` refuses prompts with "in the style of", "like" and a name,
"cover of", quoted titles and genres named after a person, and says why. Lyrics must be the user's own or written for
the job.

**Honest provenance.** The Prohibited Use Policy also bans misrepresenting where content came from by claiming it was
made only by a person in order to deceive. Background music needs no label on its own, but never claim it was
composed by hand.

## Sound effects

| Source | Licence | How nexa-sound uses it |
|---|---|---|
| The built-in synthesiser | made by the skill's own code: no samples, no third-party rights | first choice for every preset name; free to use in any work |
| Your own folders (`NEXA_SFX_DIRS`) | whatever you recorded in the folder's `manifest.json` | used in place; `CREDITS.txt` flags a licence that is not recorded |
| media-use's bundled effects | Pixabay Content License: free for commercial use, no attribution needed; the files may not be redistributed on their own, and trimming or filtering them does not change that | used in place, by path, inside the mix; never copied into a project or deliverable folder, never into a public repo |
| Freesound | per sound; nexa-sound searches with `license:"Creative Commons 0"` | CC0 by default; CC BY only when a cue allows it, and then `CREDITS.txt` lists the credit line to paste; NC never. Downloads are the 128 kbps previews (the original file needs OAuth2) |
| ElevenLabs Sound Effects | commercial use on paid plans (check your plan's terms) | only with `ELEVENLABS_API_KEY`; the account's plan is checked first and the free plan is refused |

## Never used for client work, and why

| Source or model | Why not |
|---|---|
| MusicGen, AudioGen (Meta) | weights under CC-BY-NC-4.0: non-commercial only. The media-use skill falls back to MusicGen for music; nexa-sound never does |
| MMAudio | CC-BY-NC-4.0: non-commercial only |
| AudioLDM 2 | CC-BY-NC-SA-4.0: non-commercial only |
| TangoFlux | "for non-commercial research use only" |
| ThinkSound | its README says research and educational use only, despite an Apache-2.0 tag on the code |
| HunyuanVideo-Foley | a community licence with territory and use restrictions: avoided |
| BBC Sound Effects | the RemArc licence covers personal, educational and research use |
| Freesound sounds under an NC licence | non-commercial by definition; the search filter and a second check on each result exclude them |
| ElevenLabs on the free plan | its output is not for commercial use (check ElevenLabs' current plan terms) |
| Any sound "from YouTube" or a streaming service | no licence to reuse it |

## What nexa-sound records

- `<id>.json` per Lyria track: provider and model, the key's variable name (never the key), the exact prompt and
  images, every text part the model returned, the original's SHA-256, C2PA presence, the analysis, fits, QC and the
  licence summary. `<id>_orig.*` stays untouched and read-only.
- `ledger.jsonl`: every paid call with its estimate.
- `<stem>_cues.json`: each effect's source, file, licence and any credit line.
- `CREDITS.txt`: all of it in plain words for the client.

## Sources

- Gemini API Additional Terms of Service (updated 2026-04-28): https://ai.google.dev/gemini-api/terms
- Google Generative AI Prohibited Use Policy (in force 2026-09-25): https://policies.google.com/terms/generative-ai/use-policy
- Google Cloud, Generative AI Indemnified Services (last modified 2026-07-20):
  https://cloud.google.com/terms/generative-ai-indemnified-services
- Google DeepMind, SynthID: https://deepmind.google/models/synthid/
- Google, Generate music with Lyria 3.5 (limitations, SynthID; updated 2026-09-23):
  https://ai.google.dev/gemini-api/docs/music-generation
- Google Cloud, Lyria 3 model page (C2PA and watermarking; updated 2026-09-24):
  https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3
- Google Cloud blog, Lyria 3 models on Vertex AI (training data and filtering; 2026-04-08):
  https://cloud.google.com/blog/products/ai-machine-learning/lyria-3-and-lyria-3-pro-on-vertex-ai
- US Copyright Office, Copyright and Artificial Intelligence, Part 2: Copyrightability (2025-01-29):
  https://copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf
- YouTube Help, disclosing altered or synthetic content: https://support.google.com/youtube/answer/14328491
- Pixabay Content License summary: https://pixabay.com/service/license-summary/
- Freesound API authentication and search: https://freesound.org/docs/api/authentication.html
- ElevenLabs sound effects API: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
- Model cards read on Hugging Face (2026-09-25): facebook/musicgen-small, facebook/audiogen-medium, hkchengrex/MMAudio,
  cvssp/audioldm2, declare-lab/TangoFlux, tencent/HunyuanVideo-Foley; ThinkSound README:
  https://github.com/FunAudioLLM/ThinkSound
