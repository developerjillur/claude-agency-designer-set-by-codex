# Changelog

## 2026.09.26.1

First release of the nexa-remotion family: a director skill, eleven craft skills and a tested kit for Remotion
4.0.528.

- Research: every page of the Remotion docs (1,103), the rest of remotion.dev (182 pages), the monorepo's plugins,
  skills, evals, MCP server, example project, team videos and 20 templates, 32 example repositories and the community,
  read in full and written up in 13 files (`references/kb/`), with version gates for 4.0.528.
- Kit (`kit/`): core (formats and safe areas, the size unit, 20 themes, 45 font families with their real weights and a
  Bangla fallback in every stack, named curves and measured springs, seeded randomness, beat grids, reading time) and
  motion (Animate with 19 reveals and exits that end on the last frame of their Sequence, Stagger, Camera with
  parallax, PushIn, Shake, Float, MotionBlur), plus the type, design, graphics, ui, maps, three, fx and edit modules,
  each with a README and a demo per component.
- `nrk.py`: doctor, setup, new, stills (labelled contact sheets), still, render presets (web, draft, master, alpha,
  webm-alpha, gif, all bt709 and `--gl=angle`), qa, demos (per module or the whole kit), sync.
- Skills: `nexa-remotion` (director: intake, treatment, words, voice-first timing, storyboard with frame arithmetic,
  build, look, independent review, delivery) and `nexa-remotion-motion`, `-type`, `-design`, `-graphics`, `-ui`,
  `-maps`, `-3d`, `-fx`, `-edit`, `-render`, `-styles` (27 named looks).
- Agents: `remotion-director` (brief to delivery on its own) and `remotion-reviewer` (a fresh critic that sees only the
  render).
- Evals: 12 real-world briefs with observable pass conditions (`evals/scenarios.json`).
- Proved on three finished videos (`examples/`): a 24 s Bangla vertical tip video, a 33 s English map story and a 27 s
  SaaS launch, each with voice or music, sound effects, a mix at -14 LUFS, measured QA with no flags and two rounds of
  independent review. What they taught is in `references/field-notes.md`.
- Kit fixes from those builds: push-in cards (TitleCard, SectionTitle, EndCard) anchor their push on their text edge,
  so text at the safe edge stays inside it; `LogoMarkView` draws a logo mark still (end card logo slots); the Animate
  mask travels its box plus both paddings (no glyph peeks through at rest); `SafeArea` has a 4 px inset for glyph
  overhang; themes carry `accentText` and an `onAccent` at 4.5:1 or better, and `grainRate`; core exposes
  `waitForKitFonts` and `useFontsReady`; motion has `useLife`, `frameAtProgress` and `ZoomAt`; `beatGrid` no longer
  drifts; `nrk.py new` copies the kit's runtime sounds into the project; contact sheets put labels under the frames.
- Kit fixes from the reviews: the dhaka and corporate themes set Bangla text in Noto Sans Bengali (Hind Siliguri
  draws the digit one as a hook); `TikTokCaptions` takes `sentenceMs` (pages by phrase, never mid-phrase) and gives
  complex scripts a taller pill; `Animate` exits and `DeviceRise` fade on an even curve (an ease-in fade read as a
  blink and made a brightness jump); map pins and labels stay by default, so the last frame is never half-faded;
  a route draws every casing under every line (no light gaps at waypoints); the end card's pointer clicks the arrow,
  never the label, then moves off; `nrk.py stills --guides` draws the safe area on the sheet; `nrk.py render --preset
  upload` (CRF 12) for files a platform re-encodes. From the second review: caption lines never end on a word that
  belongs with the next (Bangla determiners, numbers, English small words; `layoutText` takes `noBreakAfter`); map
  labels fade when the safe area pushes them off their point instead of sliding along the edge; route stop pins
  leave with the route; `FormField` labels grow with the field; the end card's address and handle are larger.
- Found on the way: Remotion refuses an image-sequence folder whose path contains a dot anywhere; `remotion
  compositions --log=error` hides its table; one-frame compositions are listed as `Still`; damping above critical
  changes nothing in Remotion's spring solver.
