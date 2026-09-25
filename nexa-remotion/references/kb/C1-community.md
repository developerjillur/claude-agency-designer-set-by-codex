# C1-community: the Remotion community, motion craft and competing tools (web research)

Research agent C1-community, access date 2026-09-25. Material: the public web (GitHub repos, gists, marketplaces,
blogs, Remotion GitHub issues and Discussions, motion-design references, comparisons). Every URL read is listed in
`kb/C1-community.coverage.txt` (189 lines). Target install: Remotion 4.0.528 on React 19. Where a community claim
touches a Remotion API, I checked it against the local docs mirror or the core source and say so; unchecked claims
are marked "community claim".

Licence note for skill authors: Remotion itself is source-available. Free for individuals, for-profit
organisations with up to 3 employees, non-profits and evaluation; everyone else needs a Company License
(remotion.pro). Copying Remotion code to sell a derivative is forbidden in every tier (LICENSE.md). Blogs that
quote prices or a "BUSL / revenue threshold" model (pkgpulse, arceapps) disagree with the official text; do not
repeat prices in our skills.

---

## 1. Scope and coverage

What I read (counts):

| Kind | Count | Notes |
|---|---|---|
| GitHub repo searches | 12 query sets | `gh search repos` and `topic:remotion` (2 pages, ~120 repos ranked by stars) |
| READMEs read in full | 53 | 50 Remotion-agent projects plus HyperFrames, Revideo, Motion Canvas |
| Deep knowledge files (SKILL.md, references, rules, docs) | 63 files from 16 repos | the craft material that actually teaches (listed in coverage) |
| Remotion GitHub Discussions | 11 threads (of 110 total) | Discussions are sparse; the project's real support channel is Discord (not readable without login) |
| Remotion GitHub issues | 24 issues with comments | chosen by comment count and topic (perf, fonts, media, flicker, Lambda, alpha, audio) |
| Web articles and pages | ~27 | comparisons, tutorials, motion-design references, subtitle standards, springs, Material tokens |
| Web searches | ~30 | listed as grouped lines in the coverage file |
| Local verification reads (not web) | about 11 docs pages + `spring-utils.ts` | only to confirm or refute community claims about APIs and versions |

Could not read / limits:
- YouTube videos cannot be watched; I used their pages, descriptions and written derivatives only. Reddit and
  the Remotion Discord were not read (login walls). The Material 3 motion page is script-rendered, so token values
  come from Google's own `material-web` token source. The Ripple Training article returned no body.
- Two strong repos are PolyForm Noncommercial (Vincentwei1021 `anything2explainer`, `video-talkcraft`) and two
  are AGPL (OpenMontage, OpenChatCut): learn from them, never paste their text or code. The official
  `remotion-dev/skills` repo has no licence file; several community repos vendor stale copies of its rules
  (30x-video, ECC `remotion-video-creation`, mcp-use rule tools, buainoai, jdrhyne): treat those copies as
  outdated mirrors, not sources.
- Several READMEs contain text addressed to agents (OpenMontage: "If you're an OpenClaw agent reading this...";
  video-shotcraft SKILL.md asks the agent to promote the author's accounts after delivery). I treated all of it as
  data. Our skills must not carry such self-promotion steps.
- Many repos are Chinese-language (video-talkcraft, anything2explainer lessons, shotcraft rules, remotion-director
  protocols, erduo). Read in the original; summarised in English here.

---

## 2. Mental model

1. **Remotion is never the bottleneck; craft and verification are.** Every serious community project (haidrrrry,
   agentic-product-demo, product-launch-motion, 30x-video, remotion-director, shotcraft) converged on the same
   diagnosis: an agent writes valid Remotion code easily, and the output still looks like a template because of
   default easing, simultaneous entrances, centred small objects on flat backgrounds, unreadable holds, invented
   UI and unmeasured sound. The fixes are craft rules plus render-and-look loops, not more API knowledge.

2. **Two opposite failure modes bound good motion** (product-launch-motion, 04-motion-grammar):
   - *Slideshow*: everything lands at once, then nothing happens (one stagger at t=0, timeline finished at 15% of
     the shot).
   - *Screensaver*: everything drifts independently forever (infinite loops, breathing, a push that never ends).
   The target is several cued events that each complete, then a still read. anything2explainer found the same
   pair in production ("enter-then-freeze" vs "land-then-cut") and fixed both with numeric rules (no full
   stillness over 3 s, 30-45 frames of settled hold before every exit).

3. **Time has one source of truth, chosen in this order:** spoken words (measured word timestamps) > music
   (measured beats/energy, only if the track is rhythmic) > reading time (for silent cards). "Every reveal is
   cued to the thing that motivates it"; a frame number that cannot be traced to a word, a beat or a reading
   budget is a guess.

4. **Preview is not the render.** The Player/Studio re-renders on the display clock (a 30 fps comp on a 120 Hz
   screen must hold each frame for 4 refreshes; missed budgets look like judder), uses native elements, clamps
   audio volume to 1, and can hide transparency and font problems. Sign-off happens on the encoded file.

5. **An agent cannot reliably grade its own render while its design intent is in context** (remotion-director,
   seen three times on three briefs). A design-blind critic that sees only frames plus the one-line brief finds the
   flaw in seconds. How frames are sampled decides whether that critic judges design or hallucinates defects
   (sample pauses as "held" frames; mark mid-motion frames as motion-only).

6. **Evidence, never grep.** Visual and timing claims are only proven by rendered pixels (stills read at full
   size, crops of dense type, frames at cut boundaries) and audio claims only by measurements of the delivered
   file (loudness, cue-window peaks, envelopes). Source-code pattern checks prove structure, not quality
   (30x-video qc-gates). Deliveries end with an honest "what I did not verify" list.

7. **Design from the product's truth, not from a house style.** Real logos, real UI copy, real numbers, the
   brand's own tokens and curves. Invented UI and fake metrics are the loudest "AI made this" tells. Prohibition
   lists alone converge every model to the same ugliness (remotion-director's first dead architecture); pair bans
   with positive equipment (a falsifiable conceit, composition/typography/colour knowledge) and with divergence
   (three directions, kill two).

8. **Distribution model of the ecosystem:** copy-paste component registries (shadcn CLI or own CLI) with agent
   skills, `llms.txt` files and MCP search tools are the dominant community pattern (remocn, snapcn, RemotionUI,
   remotion-bits, Onda). Official Remotion MCP is deprecated in favour of Agent Skills (`npx remotion skills add`,
   or `npx skills add remotion-dev/skills`).

9. **Remotion vs its rivals is an authoring-model choice.** Remotion: React, frame as a pure function, mature
   Lambda/Cloud Run. HyperFrames: plain HTML plus seekable GSAP/CSS/Lottie timelines, Apache-2.0, agent-first.
   Motion Canvas/Revideo: generator-based canvas scripts (MIT). After Effects: GUI keyframes plus expressions, not
   agent-drivable. Details in section 3.D and 7.K.

---

## 3. API digest (community tools, and Remotion facts the community gets right or wrong)

### 3.A Community component libraries and registries (what to reuse or learn from)

| Project | Licence | Install / API shape | What is good in it |
|---|---|---|---|
| remocn (Remocn/remocn, 1.5k stars) | MIT | `npx shadcn@latest add @remocn/<name>`; skill `npx skills add Remocn/remocn` | Copy-in primitives (blur-reveal, wipes, kinetic titles), no `Math.random`, live scrubbable previews |
| snapcn (snapcndev/snapcn) | MIT | `npx shadcn@latest add @snapcn/<name>`; 21 components (answer-stream, terminal-simulator, phone/laptop frames, karaoke/word captions, logo-assemble); needs `components.json` and the `@/` alias in both tsconfig and `remotion.config.ts` (the bundler does not read tsconfig paths) | Measured motion-quality rules (text judder, easing freeze), anti-pattern list, archetype docs, `llms.txt` |
| RemotionUI (riaz37/remotion-ui) | MIT | `npx remotion-ui@latest init --existing --agent-skill`; `search -q <x> --json`, `add`, `diff`, `doctor`; also `@remotionui/<name>` via shadcn; MCP server | 206 components in lanes (scenes, primitives, data, transitions, paths, maps, shaders, 3D); every component render-verified (catches frozen tails, `delayRender` gaps on map tiles, `Math.random`) |
| remotion-bits (av/remotion-bits) | MIT per README (GitHub shows none) | `npx remotion-bits find "<goal>" --tag scene-3d --json`, `fetch <id> --json`; MCP `npx -y remotion-bits mcp` exposing `find_remotion_bits`, `fetch_remotion_bit`; jsrepo registry | Search-by-visual-goal for agents; one shared catalog behind docs, CLI and MCP |
| Onda (degueba/onda) | MIT (brand excluded) | `npx ondajs add <name>`; `ondajs/motion` exports `entryFadeRise`, `heroReveal`, `stateSwap`, tokens `DURATION`, `SPRING_SMOOTH`, `STAGGER`, `HOUSE_EASE` | A written motion language: overdamped house spring `{damping:200, stiffness:100, mass:1}`, `HOUSE_EASE = Easing.bezier(0.16,1,0.3,1)`, entrances 18-28 f, exits 12-18 f, stagger 3-5 f, travel 12-24 px; Zod schema per component; THEME CSS variables for brand re-skin |
| @curvable/motion | MIT | `npm i @curvable/motion`; each component exports `X`, `XProps`, `XDefaults`, `XMeta {width,height,fps}`, `computeXDuration(params)`; one `primary` hex derives all shades in HSL | The best API convention for agents: no agent invents timing or colours; duration is computed from the same props |
| remotion-animated (stefanwittwer) | MIT | `<Animated>` declarative JSX animations | Older; shows a declarative alternative to per-element interpolate |
| lifeprompt-team/remotion-scenes | MIT | 201 scenes in 16 categories via `npx degit` | Breadth reference (themes, rollers, liquid, cinematic titles) |
| RVE remotion-templates, RenderComp free templates, locomotion, ali-abassi/remotion-templates | MIT / MIT / none / none | single-file templates; ali-abassi ships 1,000 templates in 100 families plus an agent catalog JSON and a render-smoke gate | Coverage maps of what people ask for (charts, logo reveals, lower thirds, transitions, social frames); ali-abassi's "inspect previews, copy recipe, typecheck, focused render" loop |
| video-shotcraft (Vincentwei1021) | Apache-2.0 | 157 shot recipe cards, 214 motion previews, deterministic TSX demos driven by normalised progress `t`, one swappable `ACCENT` | The richest reusable motion vocabulary under a permissive licence; each card has purpose, energy, duration, parameters, pitfalls |

### 3.A2 End-to-end agent skills and pipelines (what they do, licence, what is worth taking)

| Project (stars at access) | Licence | What it does | Worth taking |
|---|---|---|---|
| calesthio/OpenMontage (61k) | AGPL-3.0 | agent-orchestrated production system: 11 pipelines, 100+ tools, YAML manifests + markdown director skills, Remotion or HyperFrames or FFmpeg | stage order research -> proposal -> script -> scene plan -> assets -> edit -> compose; slideshow-risk scoring; budget caps; runtime locked at proposal; post-render verification (ffprobe, frames, transcript of the render) |
| Vincentwei1021/video-shotcraft (9.5k) | Apache-2.0 | cinematic product promos from 157 shot cards and a validated 36 s template; browser workbench after delivery | case-law aesthetic rules, beat-grid fitting, SFX taxonomy, "independent final review by a clean-context sub-agent" |
| digitalsamba/claude-code-video-toolkit (2.1k) | MIT | explainer/sprint-review workspace: commands `/video`, `/scene-review`, `/design`, brand profiles, cloud-GPU tools (Qwen3-TTS, FLUX.2, ACE-Step, LTX-2) | multi-session `project.json` reconciling plan vs files; brand profile folder; custom transitions (glitch, rgbSplit, zoomBlur, lightLeak, clockWipe, pixelate, checkerboard) |
| Vincentwei1021/anything2explainer (2k) and video-talkcraft (1.2k) | PolyForm NC | topic -> narrated explainer; script + voice -> talking video with 108 motion cards | read-only: nine-stage pipeline with four human checkpoints, parallel build agents per shot group, QC metrics, per-word alignment (20-40 ms median) |
| Agents365-ai/video-podcast-maker (1.6k) | MIT | topic -> 4K narrated video with Edge/Azure TTS, platform publish info | human script-polish checklist; length budgets (~150 English words/min, ~280 Chinese chars/min) |
| 0xsline/OpenChatCut (2k) | AGPL-3.0 | local agent-native timeline editor with MCP edit sessions | draft-then-approve edit model, face-safe caption placement |
| Remocn, snapcn, RemotionUI, remotion-bits, Onda | MIT | component registries (3.A) | reuse parts; copy their motion tokens and render-verification habits |
| haidrrrry/claude-remotion-skill (197) | MIT | one motion-graphics skill: 10 rules, 17 patterns, render -> inspect -> fix loop | good starter patterns (grain, vignette, Ken Burns, captions); some rules are one house style (7.J) |
| Liamrjohnston/remotion-motion-graphics-skill (71) | MIT | four skills: gate, cinematic camera, terminal inserts, article highlights; executable research and critic gates | "never restate the voiceover on screen"; zero-neon policy; critic thresholds |
| Alexwtlf/agentic-product-demo (311) | MIT (per README) | product demo clips rebuilt from the product's source, frame gate | nine motion rules; token adoption from the app stylesheet (`npm run adopt`); preview contact sheets |
| norahe0304-art/30x-video (63) | MIT | URL -> 40 s launch film via deterministic brand harvest and a 16-law taste codex | composition laws, four evidence gates, honest disclosure, beat-sync modes |
| AbubakrChan/product-launch-motion (64) | MIT | launch films in HTML+GSAP rendered by HyperFrames, laws portable to Remotion | the most rigorous trap file in the ecosystem |
| crimeacs/product-demo-director (27) | MIT | product films from captured footage or motion-graphics track, with preflight, QA, judge | story grammars, judge statistics, redaction rules |
| noamdorr/saas-product-demo-video (59) | MIT | 20-45 s SaaS demo skill with librosa beat sync and schematic UI | click positioning, writing-style check (no em dashes), vertical port |
| hassancs91 claude-youtube-editor (312) and faceless-shorts-creator (263) | MIT | talking-head edit pipeline; three shorts tracks (TSX, generative, collage) | shorts grammar, SFX library with loudness-normalised catalog, audibility checks |
| Zane-0x5a/remotion-director (32) | MIT | brief -> motion piece via N draws, blind select, blind critic loop, tempo pass | the review architecture |
| EveryInc/product-launch-video (47) | MIT | 15-30 s launch skill with 4 parallel critics (design, readability, pacing, brand) | product on screen within 3 s, text readable at 720p, burned captions for muted viewers, real UI copy only |
| AmazingAng/ccvideo (20) | MIT | promo videos generated from ground truth captures of real CLI or Claude Code sessions | `verify-props` rebuilds props from raw captures and fails on any hand-edited number |
| DojoCodingLabs/remotion-superpowers (125), Hainrixz/editor-pro-max (252), jhartquist/claude-remotion-kickstart (119), runesleo/claude-video-kit (120) | MIT (editor-pro-max: NOASSERTION) | plugin with 5 MCP servers; editor with 25 components and silence/whisper scripts; starter kit; JSON-script explainer with pre-render review receipt | review-before-render receipts (claude-video-kit), `/review-video` loop idea |
| gyoridavid/short-video-maker (1.4k) | MIT | REST+MCP shorts generator | resource-constrained render settings |
| erduo1998-cell/erduo-broll-loop-engineering (197), notivn/AIEV (121) | MIT | SRT-driven B-roll with Director/Creator/Reviewer roles (HyperFrames default); Claude-directed HyperFrames scenes + Remotion assembly | erduo's record: technical checks passing did not produce acceptable visuals; independent reviewer on real media is required |

### 3.B MCP servers and agent integrations seen in the wild

- Official: "Remotion's Model Context Protocol" is deprecated; Remotion points to Agent Skills.
- `remotion-media-mcp` (stephengpope): tools `generate_image`, `generate_video_from_text`, `generate_video_from_image`,
  `generate_music`, `generate_sound_effect` (0.5-22 s, loop flag), `generate_speech` (21 voices, speed 0.7-1.2),
  `generate_subtitles` (local whisper), asset library tools; writes into `public/` for `staticFile()`.
- `remotion-mcp-server` (PratyushChauhan): `remotion_create_project` from JSON-parameterised templates,
  `remotion_render` with quality presets (draft = JPEG 60 / 2 cores ... ultra = 100 / 16 cores), status polling,
  base64 asset upload, `remotion_preview` starting Studio.
- `remotion-mcp-app` (mcp-use): one model-visible tool `create_video({files, entryFile, durationInFrames, fps,
  width, height})` compiled by esbuild in under a second and played inline; the mounted view adds an ephemeral
  `update_video` that sends only changed files. Useful pattern: a live player inside chat for fast iteration.
- `chuk-motion` (IBM, Apache-2.0, Python): design-token-first MCP; tools like `remotion_add_pie_chart(...)`,
  track-based timeline (main auto-stacks with 0.5 s gap, overlay layer 10, background layer -10), time strings
  (`"1.5s"`, `"500ms"`), platform safe-margin tokens.
- `short-video-maker` (gyoridavid, MIT): REST+MCP; Kokoro TTS + whisper.cpp + Pexels + Remotion; runs with
  `CONCURRENCY=1` and a 2 GB OffthreadVideo cache to avoid OOM on small machines.
- OpenChatCut (AGPL): editor with Streamable HTTP MCP where external agents open `begin_edit_session`, edit an
  isolated draft, then `review_edit_session`; applied atomically as one undo step. Good model for safe agent edits.
- `npx skills add <owner/repo>` (vercel-labs skills CLI) is the de facto installer for community skills across
  40-60+ agents; Claude Code plugin marketplaces are the second channel.

### 3.C Remotion API facts the community relies on (verified against the 4.0.x docs mirror or source)

| Fact | Status | Version / detail |
|---|---|---|
| `fade()` leaves the exiting scene fully opaque by default (`shouldFadeOutExitingScene`, default `false`) | verified | option since v4.0.166. Two centred transparent scenes crossfading are both legible for the whole overlap; use `slide()`/`wipe()`, opaque scenes, or set the option |
| Inside `<Sequence>`, `useVideoConfig().durationInFrames` is the Sequence's end in local frames (accounts for `playbackRate`, `trimBefore`) | verified | OpenMontage's "#1 footgun" (returns composition length) and iart's "use it for absolute timing" are wrong for current versions |
| Composition IDs may contain only letters, numbers and `-` | verified | underscores fail; "PascalCase only, no hyphens" (vidtsx skill) is a VidTSX rule, not Remotion's |
| `spring()` physics run in seconds: `omega0 = sqrt(k/m)` rad/s, `t = frameDelta/1000` ms->s; default `{damping:10, mass:1, stiffness:100}`; results cached per (frame, fps, config) | verified in `spring-utils.ts` | Apple's duration/bounce formulas therefore map directly (recipe 4.1) |
| `interpolate()` per-segment easing arrays | verified | v4.0.462 |
| `interpolateColors()` accepts `oklch()` | verified | v4.0.439; its own `easing` option v4.0.475 |
| `iris()` presentation | verified | v4.0.316 |
| `useCurrentScale()` for measuring under Studio zoom | verified | v4.0.125 (Discussion #3421 is the origin story) |
| `<HtmlInCanvas>` (DOM into canvas, WebGL post) | verified | v4.0.455; Studio preview needs Chrome 149+ with `chrome://flags/#canvas-draw-element` |
| `@remotion/media` `<Video headless>` and `onVideoFrame` | verified (`headless` v4.0.387) | community: `<OffthreadVideo onVideoFrame>` needs 4.0.190+; the callback gets an `HTMLVideoElement` in preview and an `HTMLImageElement` in render (Discussion #5121) |
| ProRes alpha needs `proResProfile: "4444"` (camelCase R) with `pixelFormat: "yuva444p10le"` and `imageFormat: "png"` | issue #6235 | a typo `proresProfile` silently produced profile 3 without alpha; use the type checker |
| `volume` above 1 amplifies in the render (Web Audio gain) but preview clamps to 1 | community (shotcraft, source-checked by its author) | judge loudness on the render |
| `getRemotionEnvironment().isRendering` | community (snapcn) | used to gate `will-change` to preview only |

### 3.D Competing tools, API shape in one glance

- **HyperFrames** (heygen-com, Apache-2.0, 53k stars, Node 22+): HTML file whose DOM declares timing:
  `class="clip" data-start data-duration data-track-index`, `data-volume` on media, one paused GSAP timeline per
  composition registered as `window.__timelines[id]`, built synchronously. Media discovered by `id` (an `<audio>`
  without id renders silent). CLI `init / lint / check / snapshot / preview / render`, registry `hyperframes add`,
  AWS Lambda and HeyGen cloud rendering. 21 agent skills (router `/hyperframes`, `/product-launch-video`,
  `/motion-graphics`, `/music-to-video`, `/remotion-to-hyperframes`, ...). Its own guide says a migration skill
  translates about 80% of Remotion mechanically; the rest is `useState/useEffect` machinery, async metadata and
  React UI libraries.
- **Motion Canvas** (MIT, 19k stars): TypeScript generator scenes (`yield* node().scale(2, 1)`), canvas renderer,
  real-time editor, strong for voice-over-synced vector explainers; exports image sequences.
- **Revideo** (now `midrender/revideo`, MIT, 4k stars): Motion Canvas model plus headless `renderVideo()`, render
  endpoint, parallel workers, React player; telemetry on by default (`DISABLE_TELEMETRY=true`).
- **After Effects**: GUI keyframes + JS expressions (`wiggle`, `loopOut`, `valueAtTime`, `seedRandom`); not
  agent-drivable (product-launch-motion's bake-off ruled it out); its expression idioms translate to Remotion
  (recipe 4.14).

---

## 4. Recipes (concrete, with Remotion shapes)

### 4.1 Springs from "duration + bounce" (Apple WWDC23 model)
Apple configures springs with a perceptual duration `d` (s) and `bounce` in [-1, 1]; bounce 0 = critically damped
(smooth, no overshoot), about 0.15 = subtle, 0.3 = playful, above 0.4 reads exaggerated. With mass 1:
stiffness = (2 pi / d)^2; damping = (1 - bounce) 4 pi / d for bounce >= 0, and 4 pi / (d (1 + bounce)) for bounce < 0.
Remotion's solver uses seconds, so this maps 1:1:
```ts
const appleSpring = (d: number, bounce = 0) => ({
  mass: 1,
  stiffness: (2 * Math.PI / d) ** 2,
  damping: bounce >= 0 ? ((1 - bounce) * 4 * Math.PI) / d : (4 * Math.PI) / (d * (1 + bounce)),
});
// spring({frame, fps, config: appleSpring(0.5, 0)})  -> stiffness ~158, damping ~25
```
Use `measureSpring()` (or `durationInFrames` on `spring`) to budget the settle inside a Sequence.

### 4.2 Scaled text that does not stick or shake (snapcn, measured)
- Scale type about its **baseline** (measure it with a zero-size inline-block on the baseline); vertical judder
  fell from 0.284 px (centre pivot) to 0.014 px (baseline pivot).
- `textRendering: "geometricPrecision"` switches off hinting; glyph shape drift under scale fell from 3.41% to
  0.22%, and it forces subpixel glyph positioning which a DPR-1 render otherwise lacks.
- Never `will-change: transform` on text in the render (parallel tabs keep stale rasters; byte-identical styles
  produced 4 different rasterisations and ~9,000 changed pixels per held frame). Gate it:
  `...(getRemotionEnvironment().isRendering ? null : {willChange: "transform"})`.
- Cargo cult that does not fix it: `translateZ(0)`, `backface-visibility`, `perspective(1px)`, `blur(0px)`,
  font-smoothing; animating `font-size` is worse (reflow plus snapping).
- Slow sub-pixel drifts of text look choppy (issue #4738). Hold text still while it is read (remotion-director
  tempo rule) and put the drift on the camera or background instead.

### 4.3 Titles: words, masks, no fades (agentic-product-demo, product-launch-motion)
- Per word, not per letter: "AI Film Director" per letter at a 2-frame stagger needs 30 frames before the last
  glyph moves; per word (3 words, 3-frame stagger, 15-frame rise) lands at frame 24 and leaves a second of
  stillness. Wrapping glyphs in boxes also destroys kerning. Per letter only for a 4-5 glyph wordmark.
- Mask, never fade: each line in its own `overflow:hidden` box, the word rising from `translateY(110%)`; adding
  opacity on top defeats the mask. Negative tracking on large titles (-2.5 px at 92 px) reads "set, not typed".
- Line-by-line kinetic paragraphs: enter each line on its word (0.30 s, 28 px rise), demote spent lines to about
  0.30 opacity and nudge the stack up about 10 px per arrival.

### 4.4 Counters and typewriters
Drive discrete values from frame-pure math, snap to integers, use `fontVariantNumeric: "tabular-nums"`, grow the
numeral with `scale` not `font-size`, start on the word that names the number and settle before the next clause.
Mind intermediate values: a count 1995->1998 shows 1996/1997 legibly; if those are not facts, blur the roll or do
not count (anything2explainer). Typing budget: `start + chars x framesPerChar + pauses <= sceneDuration`
(noamdorr), floor about 0.5 f/char.
```tsx
const p = interpolate(frame, [start, start + 22], [0, 1], {easing: Easing.out(Easing.cubic), extrapolateLeft: "clamp", extrapolateRight: "clamp"});
const shown = Math.round(p * target).toLocaleString("en-US");
<span style={{fontVariantNumeric: "tabular-nums"}}>{shown}</span>
```

### 4.5 Deterministic "life" without loops (bounded sine driver)
Instead of infinite breathing, run one bounded phase: `s = 1 + 0.09 * Math.sin(Math.PI * clamp01((frame - f0)/6))`
returns to rest by construction (half cycle = pulse, full cycle = settle). Envelope any idle that runs into a hold
so the cut does not chop it. At most one element alive during a hold, the hero. For organic wiggle use
`@remotion/noise` (`noise2D(seed, t * freq, 0) * amp`), low frequency 0.3-0.6 Hz and 4-10 px, and only on things
that are not being read.

### 4.6 A camera through one world (Liamrjohnston cinematic-camera, snapcn MOTION.md)
Build a world 2-2.5x the viewport; drive focal x, y and zoom from one shared keyframe table with
`Easing.inOut(Easing.cubic)`; repeat keys to hold; moves 14-24 frames; end on two near-identical keys so an editor
can cut anywhere. snapcn tokens at 30 fps: travel 8-14 f, settle 10-16 f, text hold 30-45 f, settle spring
`{damping:18, stiffness:140}`, card pop `{damping:12, stiffness:180}`, stagger 3-6 f; motion blur on fast camera
travel (`@remotion/motion-blur` `CameraMotionBlur`/`Trail`).
```tsx
const k = [0, 46, 62, 96, 132, TOTAL];
const o = {easing: Easing.inOut(Easing.cubic), extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
const fx = interpolate(frame, k, FX, o), fy = interpolate(frame, k, FY, o), z = interpolate(frame, k, Z, o);
<div style={{position: "absolute", transformOrigin: `${fx}px ${fy}px`,
  transform: `translate(${W / 2 - fx}px, ${H / 2 - fy}px) scale(${z})`}}>{world}</div>
```
Rules that prevent drift and judder (product-launch-motion): two nodes (outer = dolly scale, inner = turn), never
two tweens on one transform; set `transformOrigin` only when scale = 1 and translate = 0; put the zoom origin
exactly on the control being clicked (it becomes a fixed point, so cursor coordinates stay valid); keep cursor,
effects and UI inside the rig; compute the keep-out ceiling before choosing a scale:
`bottom_after = bottom + (bottom - origin_y) * (scale - 1)`. Never keep a lasting transform on the container that
holds a whole UI (it resamples every glyph); move what is inside the frame instead.

### 4.7 The fake cursor as a stage prop
- Size about 44x54 px at 1080p (life-size 32 px disappears), white fill, dark 1.6 px stroke, real drop shadow;
  one cursor design for the whole film; position by the tip (element = click point minus tip offset).
- Path: a tiny anticipation (about 8 px, 0.05 s) then x and y on different eases/durations so the path bows;
  start the travel early so the click lands on its word; leave a one-frame gap between butt-joined moves.
- Click stack: hover bloom leads the press by 0.1 s, press scale 0.86 over 0.06 s, release with a small
  overshoot, ring ripple; the control reacts too (depress about 6% and spring back). Size feedback to the control.
- Give every target two keyframes (arrive, then hold past the press) or the pointer starts leaving as it clicks
  (agentic-product-demo). Take coordinates from a rendered frame or from exported layout constants, never from
  mental CSS arithmetic: one production needed three master renders to hit a button estimated from padding.
  Debug overlay with red target boxes while authoring. Fade the cursor out when its work is done.

### 4.8 Word-locked sync (voice first)
Order: script -> render one audio per line (or one continuous take per argument) -> word timestamps (Whisper,
ElevenLabs `with-timestamps`, forced alignment) -> frame durations = measured VO + 0.2-0.5 s tail hold (+
transition overlap) -> only then build. Write the cue table (word@seconds) as a comment above the scene; cue the
meaning (verb or emphasis word), lead readable elements by 0.02-0.06 s, fire hits exactly on the word; one beat
carries at most two cues; weight reveals to the back half of a shot. A uniform tempo change can rescale the table;
any new voice or model requires re-transcription. Cuts land in sentence gaps (word `end` + about 300 ms), confirm
with `silencedetect`; no cut while a word is mid-utterance. Fix brand-word mistranscriptions in caption text only,
never in timestamps. Some TTS drivers ignore speed flags: verify output length, use `atempo`.

### 4.9 Beat sync (only when the track is actually rhythmic)
- Detect beats with librosa, then least-squares fit a uniform grid `t_i = t0 + i*T` to the whole beat list (the
  tempo scalar can be 2% off); accept when residuals <= +-15 ms; test 0.5x/1x/2x candidates by how often kicks land
  on integer beats; separate drums (HPSS or Demucs) for dense mixes (shotcraft).
- Write the timeline in beats: `beatF = n => Math.round((BEAT0 + OUTPUT_OFFSET + n * T) * fps)`; keep the source
  analysis `BEAT0` untouched and put any measured output offset in its own constant.
- Scene boundaries on snares, internal events snapped to the nearest beat within +-6 frames (noamdorr: realigning
  17 drifting internal events was the single highest-leverage iteration).
- If the analyser says non-rhythmic, do not cut to its grid; transition on energy-phase changes, use silences as
  holds (30x-video). Narration wins over music: pick the beat nearest to the sentence gap.
- Beat sync times cuts, not amplitude: whole-frame or camera-layer hits at most 3 per film, at least 16 beats
  apart, on the strongest measured hits; everything else animates at the element layer (shotcraft R4, after a
  "the camera shakes with the beat" complaint). Never a continuous beat-synced scale throb (30x "heartbeat" ban).
- Find the climax with RMS energy (`librosa.feature.rms`, hop 256), not onsets; a transient and the swell 9-15
  frames later are two events (impact, then reveal). Do not duck music on a synced hit.
- Verify after render: extract the delivered audio, re-fit the grid, report cut error in frames (<= 3 f pass,
  <= 1.5 f ideal); 30 fps cannot claim better than +-16.7 ms visual precision.

### 4.10 Sound: arithmetic, not taste (product-launch-motion 07, shotcraft sound-design, hassancs91 suggest-sfx)
- Layers: narration loudest; music bed about 0.1-0.34 of full scale; SFX individually placed and measured.
- A cue's `volume` is a multiplier; it cannot rescue a quiet file (0.35 -> 0.85 moved the mix 0.1 dB against a
  -17 dB narration). Level the asset (trim, gain, limit) and cut from the first transient (a room-tone head made a
  typing cue cover only the back 44% of its animation).
- Verify with windows and envelopes on the delivered file: a story cue should add at least +4 dB over the
  voice-only mix in its window (texture +1-3 dB); measure clicks with about 0.3 s windows, risers in their last
  third; cues fully under continuous speech are "felt, not heard" or should be cut.
- Palette by film type, not by event: product promos use whoosh / impact / riser / sparkle / transition plus real
  foley (keyboard, shutter, switch); synthetic UI bleeps and game-pack plucks read "mobile game". One cue per
  event; nothing repeats more than twice in 45 s; anti-machine-gun: alternate two different samples, step volumes
  down (0.40 -> 0.25), tighten intervals with the motion.
- Signature phrase: riser into the build, impact on the landing about 35 frames later, sparkle 25 frames after.
  Sub-bass (quiet, long) only on thesis and CTA, with about 0.3 s of near-silence before it.
- Place SFX relative to shot starts (`SHOTS.x.from + offset` or `beatF(n)`), never as bare absolute frames;
  re-pin the whole table after any timing change; sound is done after picture lock.
- Offsets: `Sequence.from = targetPeakFrame - fileInternalPeakDelay - outputAudioOffset`; community-measured AAC
  priming around 2048 samples at 48 kHz (about 1.28 f at 30 fps) on one pipeline (see open question 3).
- Mastering: two-pass `loudnorm` to -14 LUFS integrated / <= -1.0 dBTP, then a true-peak limiter with makeup gain
  disabled (`alimiter=limit=0.891:level=disabled`), re-encode video `-crf 19 -tune film`, `+faststart`; verify
  with `ebur128=peak=true` on the shipped file. (Others master to -16 LUFS; pick one target per platform.)

### 4.11 Captions for shorts
`createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: 1200})` -> pages; every token after the
first carries a leading space; render tokens with `whiteSpace: "pre"`; active word when
`nowMs = page.startMs + frame/fps*1000` falls in `[fromMs, toMs)`. 2-4 words per page, heavy weight (72 px / 800
in snapcn's example), bottom 20% avoided on 9:16. Subtitle readability references (Netflix English): max 42
characters per line, 2 lines, up to 20 characters per second for adults (17 for children), each event 5/6 s to
7 s. Captions that function as subtitles must match speech exactly; never restate the voiceover as on-screen
headline text (Liamrjohnston rule).

### 4.12 Data visualisation
Counters: ease-out cubic, thousands separators, tabular nums. Bars: staggered springs (`{damping:20,
stiffness:100}`), labels fade with progress. Racing bars: interpolate values between snapshots per frame, sort
descending each frame, animate rank position; show at most 10-12 bars. Give chart animations at least 4 s
(OpenMontage). Numbers must trace to a source (anything2explainer); cross-check self-made example numbers against
every other label on screen.

### 4.13 Maps and 3D
Maps: keep the target route and the camera route separate; `turf.along()` for the current point; smooth the
camera with lerp so sharp turns do not jitter; reveal the line with progress (Mapbox `line-gradient` idea);
constant pitch and altitude, slow bearing rotation. 3D (`@remotion/three`): `<ThreeCanvas width height>` from
`useVideoConfig()`, animate from `useCurrentFrame()` never `useFrame()`, `layout="none"` on Sequences inside the
canvas, add lights (PBR renders black without them), drive shader uniforms from the frame, do not run GLTF
mixers on their own clock. Tone-map before bloom on near-white UI. Blurry UI on tilted 3D planes: the rasteriser
draws the layer at layout size then upsamples; raster at 2-4x (CSS `zoom` rather than transform scale) before
blaming depth of field (shotcraft Q2).

### 4.14 After Effects expressions -> Remotion
| AE | Remotion equivalent |
|---|---|
| `wiggle(f, a)` | `noise2D(seed, frame/fps*f, 0) * a` from `@remotion/noise` (seeded, deterministic) |
| `seedRandom(index, true); random()` | `random("seed-" + index)` from `remotion` |
| `loopOut("cycle")` / `"pingpong"` | `frame % period` / `interpolate(frame % (2p), [0, p, 2p], [a, b, a])` |
| inertial bounce after last key | damped sine after the landing frame: `A * Math.sin(w*t) * Math.exp(-decay*t)`, or a spring with bounce |
| `valueAtTime(time - delay)` (echo / follow) | call the same pure function with `frame - delay*fps` |
| `time * 90` (perpetual rotation) | `frame / fps * 90` |
| time remap / speed | `<Sequence playbackRate>`, `trimBefore`, `<Freeze>` |
| null + slider rig | component props + Zod `schema` (Studio edits them); one theme/tokens object |
| MOGRT essential properties | `defaultProps` + `schema`, `calculateMetadata` for data-driven duration |

### 4.15 Named-token translations (use as defaults, then tune to the brand)
Material 3 (from Google's token source): standard `cubic-bezier(0.2, 0, 0, 1)`, standard decelerate `(0, 0, 0, 1)`,
standard accelerate `(0.3, 0, 1, 1)`, emphasized decelerate `(0.05, 0.7, 0.1, 1)`, emphasized accelerate
`(0.3, 0, 0.8, 0.15)`; durations short 50-200 ms, medium 250-400 ms, long 450-600 ms, extra-long 700-1000 ms
(frames at 30 fps = ms x 0.03). Easing families (iart easing library): easeOutCubic `(0.33,1,0.68,1)`, Quart
`(0.25,1,0.5,1)`, Quint `(0.22,1,0.36,1)`, Expo `(0.16,1,0.3,1)`; exits easeInCubic `(0.32,0,0.67,0)`; moves
easeInOutCubic `(0.65,0,0.35,1)`; back `(0.34,1.56,0.64,1)`. Duration grows with distance roughly by
`sqrt(distance ratio)`; stagger total `(n-1)*offset + itemDuration` under about 800 ms.

### 4.16 GSAP inside Remotion (when an effect needs SplitText, MorphSVG, MotionPath)
Build a paused timeline once, then seek it from the frame on every render: `tl.seek(frame / fps)` or
`tl.progress(frame / durationInFrames)`; or use GSAP only as an ease calculator (`gsap.parseEase("power2.out")(t)`).
Never let GSAP run on `requestAnimationFrame`; register plugins at module scope (OpenMontage runtime selector).
Default to Remotion primitives when 20 lines of `interpolate`/`spring` do the job.

### 4.17 Grade, grain and banding
Grain as a film-like texture re-seeded at 12 Hz, not per frame: per-frame noise took a 9 MB render to 85 MB and
reads as electronic sizzle; re-encode `-crf 19 -tune film`. Vignette weak (corner alpha about 0.15). Lifted
blacks (no pure #000). Specular sweeps only on named story beats (about 3 in 45 s), skew the element instead of
angling the gradient. Gradients band in 8-bit H.264: add 2-4% grain, keep at least 2 stops, avoid huge soft
blurs (issue #3103, 30x-video). In Remotion, blend modes on overlays work (one DOM); the "film renders white"
blend-mode trap is specific to per-track compositing renderers (HyperFrames).

### 4.18 Vertical (9:16) versions
Build parallel compositions that share tokens and timing constants; horizontal is the source of truth; restack
rows into columns rather than cropping; recompute cursor paths (horizontal sweeps become vertical scrolls); use
explicit positioning with `transform-origin: center top` so zoom punches grow downward inside the safe area;
reserve at least 5% of a card's height around anything that punches (noamdorr).

### 4.19 The classic animation principles in Remotion terms
| Principle | Remotion translation |
|---|---|
| Timing | durations in frames from fps (`Math.round(seconds * fps)`); bigger or farther things get more frames (about sqrt of distance ratio) |
| Slow in / slow out | `Easing.bezier(...)` per role (4.15) or `spring()`; linear only for clocks |
| Anticipation | a 2-3 frame counter-move before committed travel (cursor pull-back about 8 px, button dip to 0.95) |
| Follow-through / overlapping action | stagger the settle of attached parts 2-4 frames after the body lands (shadow, label, badge) |
| Arcs | animate x and y with different easings or durations, or move along a path (`@remotion/paths` `getPointAtLength`) |
| Secondary action | one supporting reaction per hit (the control depresses when clicked), never a second competing primary |
| Squash and stretch | small scale asymmetry on impacts (for example 1.06 x 0.95 for 2-3 frames), consumer/playful directions only |
| Staging | one focal element; dim or blur what already paid off (rack focus: `filter: blur(2.6px)`, opacity 0.55) |
| Exaggeration | rationed to the hero beat and the signature move |
| Solid drawing / appeal | consistent light direction, real assets, typographic craft |
| Straight ahead vs pose to pose | pose to pose: keyframe tables (`interpolate` with multi-point ranges); straight ahead: frame-pure simulations with seeded noise |

### 4.20 Safe areas
Broadcast: SMPTE's legacy guides put action safe at 90% and title safe at 80% of the frame; the HD update is 93%
action and 90% title; EBU R95 for 16:9 HD is tighter (3.5% action, 5% graphics margins). For online video an 80%
title area survives phone "zoom to fill" crops (eks.tv). Vertical platforms: reserve roughly the top 12-14% and
bottom 18-20% (captions around 65% height or 20% up from the bottom), plus a right strip for TikTok buttons
(chuk-motion tokens: TikTok top 100, bottom 180, right 80 px at 1080x1920; Instagram Stories top 100, bottom
120). Critical text and logos inside the safe area for every target aspect; restack for 9:16 instead of cropping.

---

## 5. Performance and render stability

- **Concurrency is tabs in one Chrome.** Raising it gives diminishing or negative returns on big servers (issue
  #4300: a 48-core box used about 4-10% CPU; an 8-core M2 beat a 32-core server). What helped: several browser
  instances or several `renderMedia()` calls on frame ranges (`frameRange`, 3-4 tabs each) stitched afterwards,
  temp dir on a RAM disk (`TMPDIR`; about 4x faster than slow EBS), pushing simple zooms/pans into FFmpeg,
  pre-extracting heavy video to image sequences, drawing big blurs on canvas (issue #4664). Remotion's long-term
  answer is the WebCodecs-based `@remotion/media` video.
- **OffthreadVideo extraction is sequential per stream**; many videos at high concurrency bottleneck the
  compositor. Re-encode stock with dense keyframes (`-g 30 -keyint_min 30 -sc_threshold 0`): sparse-keyframe
  sources have crashed the compositor (issue #7153) and stall HyperFrames renders.
- **Low-core and CI boxes:** "Maximum for --concurrency is 2" on 2-core Linux, use `--concurrency=1`; two parallel
  renders on Apple Silicon at concurrency 8 each can hang (serialise or drop to 4); `short-video-maker` uses
  concurrency 1 plus a 2 GB OffthreadVideo cache to fit 3-4 GB RAM.
- **Browser/GL:** without `--gl=angle`, Remotion falls back to SwANGLE software GL (slower for GPU effects);
  but `@remotion/media <Video>` hung under `angle` on Windows Intel (issue #10701; workaround `--gl=swangle`),
  and timed out in Docker above 16 GB memory limit (issue #10909, open at 4.0.517). Recent Chrome dropped old
  headless: use `chrome-headless-shell` via `npx remotion browser ensure` or `--browser-executable`. "Timed out
  connecting to the browser" with an empty log is often a second Chrome instance when `CHROME_PATH` points at the
  running desktop Chrome.
- **Expensive CSS:** `backdrop-filter` and stacked large blurs made one render 4x slower for an invisible effect;
  `feConvolveMatrix` runs on a software path (0.13 fps); blur sigma under 0.8 does nothing in Chromium; prefer
  plain alpha compositing.
- **will-change:** in renders, stale per-tab rasters make held text shimmer (snapcn); yet one Lambda artifact
  (stale height/4 strips under full-width semi-transparent gradient overlays, SwANGLE) disappeared with
  `will-change: opacity` on the overlay (issue #11428). Rule: no `will-change` on text in renders; for a
  full-width overlay that ghosts on Lambda, try its own layer and compare frames.
- **Lambda determinism:** chunk-boundary differences reported for large CSS blur inside `HtmlInCanvas`
  (issue #9052, not reproduced by the maintainer); measure with `tblend=all_mode=difference` at frames divisible by
  `framesPerLambda`. A successful Lambda render could be reported as a timeout when the final progress write was
  lost (issue #7854, reported on 4.0.421 and main at 4.0.469, since closed): check the bucket for the output
  before re-rendering.
- **Player performance:** the Player re-renders the tree every frame; memoise `inputProps` (a regression thread,
  #5988, was fixed by memoisation), `React.memo` children, keep controls as siblings of the Player sharing a ref,
  animate transform/opacity, prefer native `<Video>` in the Player, `prefetch()` heavy media, `lazyComponent`
  and `Thumbnail` for grids.
- **spring cost:** each `spring()` evaluation steps from frame 0 but results are cached per (frame, fps, config),
  so repeated calls are cheap within a tab. The community claim that springs OOM long compositions (30x-video)
  is unconfirmed; do not replace springs on that basis alone.
- **Grain and file size:** see 4.17. **Fonts:** load only needed subsets (`subsets: ["latin"]`); all-subset loading
  of three families issued 21+ requests and `delayRender` warnings (noamdorr).
- **Disk:** PNG intermediates and `node_modules/.cache/remotion` grow by gigabytes on long projects; a killed
  render leaves a partial MP4 that still plays (trust only a finished render).

---

## 6. Errors and fixes (community-reported, with sources)

| Symptom | Cause | Fix | Source |
|---|---|---|---|
| Edges look aliased/fuzzy in H.264, stills look sharp | no background: PNG frames are transparent, FFmpeg flattens onto black without antialiasing | always give the composition an opaque background for H.264 (or use JPEG frames) | Discussion #3248 |
| Text soft/pixelated on phones | 1080 px video shown on 2-3x DPR screens; JPEG 80 frame capture; yuv420p chroma on coloured text; thin weights | render `--scale=2`, `--jpeg-quality=100` or `--image-format=png`, avoid thin weights, test white-on-dark to isolate chroma | Discussion #6833, issue #3715 |
| Scaled type "sticks" then jumps, letters boil | vertical glyph origin snapping, hinting | baseline pivot, `geometricPrecision`, no `will-change` in render | snapcn motion-quality |
| Word stops dead mid-rise | expo/quint ease-out tails move under 0.5 px per frame (5 of 14 frames identical) | moderate decelerate such as `(0.2, 0.6, 0.35, 1)`, check the per-frame travel | snapcn |
| Two headlines legible during a transition | `fade()` keeps the exiting scene opaque by default; transparent scenes overlap | `slide()`/`wipe()` with `springTiming({config:{damping:200}})`, or opaque scene grounds | snapcn anti-patterns, fade docs |
| Element visible before its entrance or after its exit | `interpolate` extrapolates by default | clamp both sides everywhere | many |
| Flicker/random values between frames | `Math.random`, `Date.now`, `new Date()`, CSS animation/transition, `setTimeout`, GSAP on rAF, R3F `useFrame` | `random(seed)`, frame-pure math, seek paused timelines | many |
| Logo blank for a frame | native `<img>`/`<video>` do not hold the frame | Remotion `<Img>`, `<Video>`/`<OffthreadVideo>`, `staticFile()` for assets | noamdorr gotchas |
| Works in Studio, broken in render: styles clobbered | parent app global CSS (`.card`) reaches the render bundle | namespaced classes or CSS modules | noamdorr |
| Component invisible on a site but fine in the MP4 | the site's Tailwind preflight `img {max-width:100%}` collapses a shrink-to-fit box | `max-width: none` on sized images, verify geometry in the real host | snapcn |
| Absolute child renders nothing | `inset:0` child inside a transform-only wrapper with no size | give the wrapper `position:absolute; inset:0` | noamdorr |
| SVG art cut off | SVG clips to its viewBox | `overflow: visible` or pad the viewBox | noamdorr |
| Render fails on a composition id (reported: Studio loaded, CLI render failed) | underscore in the id | letters, numbers and `-` only | noamdorr, docs |
| `npx create-video` hangs inside a repo | interactive "already inside a Git repo" prompt | use `--yes`/flags or scaffold files by hand | noamdorr |
| `em` gaps near-zero next to 150 px type | `em` resolves against the parent font size | pixel gaps in flex rows around big type | haidrrrry |
| Emoji icons ignore palette | platform colour glyphs | draw glyphs in SVG/CSS | haidrrrry |
| Frames inside `<Series>` off by the scene start | global beat frames used as local | `local = global - sceneStart`, ship `toLocal/toMaster` helpers | noamdorr, hassancs91 |
| Beat grid shifts after editing audio start | `<Audio startFrom>` changed the anchor | pre-trim audio to the drop or include `startFrom` in the beat math | noamdorr |
| Last CTA/URL unreadable | ending fade eats the final caption, glitch entrance hides half its frames | `(lastSequenceEnd - endingFade) - lastCaptionStart >= 30` frames; budget glitch reveals double | anything2explainer lessons |
| Hard cut "pops" | exit fade still at 40-60% on the last frame | `1 - (n/N)^1.5` to exactly 0 before the cut | anything2explainer |
| Text below minimum size after a group scale | transform scale multiplies effective font size | check `fontSize x all ancestor scales` against the floor | anything2explainer |
| ProRes output has no alpha | `proresProfile` typo -> profile 3 | `proResProfile: "4444"`, `pixelFormat: "yuva444p10le"`, `imageFormat: "png"` | issue #6235 |
| Render hangs "Extracting frame..." with `@remotion/media` | ANGLE decode path on Windows; Docker memory limit above 16 GB | `--gl=swangle`, or `<OffthreadVideo>`, update Remotion | issues #10701, #10909 |
| OffthreadVideo processed on canvas shows black in render | reading `readyState` on refs (render uses an `<img>`) | `onVideoFrame` callbacks, composite when both frames arrived | Discussion #5121 |
| "Rhythm sometimes feels off" | internal events a few frames off the beat | snap internal events to the nearest beat within +-6 f | noamdorr |
| SFX audible in preview, silent/quiet in file | quiet source file, volume multiplier, preview clamp | level the asset, verify the delivered window | product-launch-motion, shotcraft |
| Master clips above 0 dBFS | `loudnorm linear=true` single gain; a new transient | limiter after loudnorm with `level=disabled` | product-launch-motion |
| Stock footage shows as a small box with black bars | tiny source scaled to fit and padded | probe sources; scale-to-cover and crop (`force_original_aspect_ratio=increase,crop`) | OpenMontage |
| Mockup looks blurry under a camera zoom | transform scale of a whole UI container | move contents, not the frame; rasterise textures larger | agentic-product-demo, shotcraft Q2 |

---

## 7. What our skills must teach

### 7.A Workflow gates (in order, each producing evidence)
- **Intake:** format (aspect, size, fps), duration promise or "designer decides", audience context (muted feed
  vs conference vs sales), voice yes/no, music yes/no, brand assets available. Ask only what cannot be read from
  the product; present a pre-filled plan to correct rather than an interview (agentic-product-demo).
- **Read the product before designing:** real UI copy, real lists (grep visible strings back to their constants),
  tokens and easing curves from the stylesheet, logo files. Nothing on screen may be invented; fake dashboards,
  metrics, receipts, stamps and serials are hard failures (Liamrjohnston critic).
- **Direction:** write three directions that differ on at least four dials (energy, density, ground, depth,
  camera, type, texture, colour, product, sound, voice), plus the structural axes (device, arc, turn position,
  ending, climax mechanic, opening state, copy placement, human presence, sound dramaturgy); kill two; commit.
  If the brief matches a stock example direction, that one is automatically killed (product-launch-motion 11).
  Name one signature move that expresses the product's verb and repeats 2-3 times.
- **Storyboard as a shot list with frame arithmetic** (start frame per phase, total length shown with its sums),
  a cue table per shot, and which single element carries each shot's hero beat. Get the flow right before code:
  it is the one defect that cannot be fixed in the edit.
- **Voice first** when narrated; durations derive from measured audio. Music analysis before cutting to music.
- **Build per act, render stills per act, read them at full size** (plus crops of dense type), fix before the next
  act. Probe shared systems (camera, layout constants, shared primitives) with a one-page test render before
  parallel builders use them, and put shared helpers in one common module so builders do not reinvent them.
- **Technical QA on the delivered file:** ffprobe (streams, size, fps, duration within 5%, audio present),
  black/frozen frames, luminance jumps and loop seam, tiled/corrupt frames, last frame of every shot static,
  loudness, cue audibility windows, transcript of the rendered audio vs script (catches cut-off narration).
- **Independent visual review:** a fresh-context critic that never sees the design doc or code; sees held frames
  plus marked motion frames; must make at least 3 native-resolution crops of dense zones; reports phenomena with
  severity only; builder may rebut with pixel evidence; same critic persists across rounds; stop when nothing high
  or medium remains. Optionally N independent drafts and a provenance-blind pick for the highest ceiling.
- **Tempo pass after visual convergence:** a fresh agent rebuilds the beat timetable from the source and fixes
  dwell times without touching design; it may only redistribute time inside a promised duration.
- **Model judges are advisory:** pin the model, median of 3 runs, compare champion vs candidate in both orders,
  ship only a 2-0 winner; a judge never waives a failed deterministic gate; after three failed cut-level
  candidates stop recutting and change material (product-demo-director).
- **Delivery message:** file path(s), what was verified with counts ("9 stills of 1,200 frames"), and a mandatory
  "what I did not verify" list (audio by ear, full-rate motion, platform compression, synthetic voice
  disclosure). Keep raws and version every render; never overwrite the only copy.

### 7.B Motion defaults (30 fps; tune to brand)
- Entrances: 8-11 frames for small UI, 15-20 for cards and lines, 18-28 calm/premium; opacity plus a small
  translate (10-28 px) and optionally scale 0.9-0.99, never scale from 0, never opacity alone.
- Exits: usually none (cut on a settled frame); when needed, faster than entrances (12-18 f) with ease-in;
  anything visible at a hard cut must reach 0.
- Stagger: 2-4 f for siblings in one gesture, 5-6 f for countable lists; total arrival must finish before the next
  word cue; 4+ items: shrink the offset or split across cues. Stagger in reading order.
- Easing: ease-out for arrivals, ease-in for departures, ease-in-out for things moving while on screen and for
  camera; linear only for clocks (typewriter, marquee, counters driven by snap); bounce/elastic rationed to state
  confirmations and at most one hero per act.
- Springs: overdamped by default (Onda `{damping:200, stiffness:100}` or Apple bounce 0); snappy
  `{damping:20, stiffness:200}`; one hero with visible settle; derive custom springs with recipe 4.1.
- Holds: content settles then holds 30-45 f minimum before any exit (1.5 s for multi-word lines); reading budget
  about 0.33 s per word plus 0.3 s, never under 1.2 s for a card, longer for numbers; dense UI 90-120 f; logo 1 s
  hold after it lands. The first cut is almost always too fast: every documented revision loop asked for slower
  and longer holds, never faster (shotcraft R3, product-launch-motion v2 -> v3 +4 s).
- One focal animation at a time; at most 1-2 things moving or being read simultaneously; text is perfectly still
  while it is read; movement belongs to entrances, exits and verb-driven actions.
- No element travels more than about a third of the frame without an intermediate change (1/3 rule).
- Cuts: prefer hard cuts between kinetic-type beats; carry direction across seams (velocity-matched cuts);
  shot lengths regular (for example 36 or 48 f) and broken once on purpose for the line that matters.
- Frame 0 is the poster: open composed and legible, motion comes from inside it (no fade from black).

### 7.C Text rules
- Load fonts before first frame (`@remotion/google-fonts` with explicit weights and subsets, `@remotion/fonts` for
  local files); a font string alone loads nothing and renders a fallback.
- Minimum effective size at 1080p: narrative captions about 56 px (5.2% of frame height) for phone viewing,
  auxiliary text 32 px, UI chrome inside mockups may go down to 12-14 px because that is how software looks
  (shotcraft Q11, 30x typography). At 720p explainers the floor used was 22 px (ink-measured).
- Two families maximum; avoid Inter/Roboto/Arial as a hero face by default; weights 500-600 for heroes on premium
  films, avoid weights under 300 in motion (they flicker after compression); letter-spacing on display type no
  tighter than about -0.04em; `tabular-nums` on changing digits; one emphasis word per headline.
- Key words may be huge (200-320 px editorial moments) and may bleed off-frame when still legible; one giant word
  plus one small annotation is a complete composition (30x composition Law 3).
- CJK: line-box ascent sits ink 3-7 px low (pre-offset), curly quotes and ellipses are full-width glyphs in CJK
  fonts (use straight quotes in English films set in CJK fonts); check glyph coverage (Orbitron lacks some symbols).

### 7.D Composition and taste rules
- No vacuum: every frame sits on a lit ground (radial light with a source, texture, horizon or parallax); a flat
  solid behind small floating content fails. But light must interact with form: sourceless glow is a defect, and
  text parked in a glow core is a contrast collapse (remotion-director critic spine).
- At least one full-bleed moment per act; content box under 60% of the frame with dead margins on all sides reads
  as a slide. Premium frames keep about 40% negative space; headlines 80%.
- One focal point; the hero wins on at least two of size, contrast, position, weight; hierarchy order motion >
  size > contrast > saturation > position; grouping by proximity (inside gaps clearly smaller than outside gaps).
- Adjacent beats use different composition systems (full-bleed image with scrim, oversized type stack, horizon
  world, asymmetric offset hero, split with a hard seam, bottom-rising surface, sequenced full-screen singles);
  keep one palette, one type voice and one light language across the film.
- Anti-slop list (use as a check, not as the design): purple/blue gradients by default, three-column icon grids,
  cards on cards, gradient text, hero-metric template, glassmorphism by default, glow on everything, emoji icons,
  eyebrow labels on every section, numbered 01/02/03 scaffolding, expanding ring ripples, rhythmic heartbeat
  pulses, decorative divider bars, confetti endings, globe/network as "tech", random particles, headline over a
  full-bleed motion asset, same visual formula in two adjacent beats, cream/sand default backgrounds.
- Decide dark vs light from a written physical scene sentence; never default silently to dark (Liamrjohnston).
- Colour: one accent with a budget; tinted neutrals; interpolate colours perceptually (`interpolateColors` with
  `oklch()` since 4.0.439, or per-frame `color-mix(in oklab, ...)`); an AA-safe darker accent for small text on
  light grounds; no third hue except semantic states.

### 7.E Sound rules (see 4.10) as a checklist
Voice loudest; bed quiet; one cue per event; foley over UI bleeps for product films; measured audibility; no
duck on synced hits; offsets compensated; master measured on the shipped file; two final versions when music is
used (with and without BGM from the same timeline via a boolean prop); licences recorded per file.

### 7.F Verification tools the skill family should ship (all exist in community form)
- Stills at beat frames plus 12 frames later tiled into a contact sheet (preview before render); full-size stills
  for judging scale (contact sheets misjudge scale).
- Frame gate: tiled-frame detector (half vs half similarity on contrasted frames), luminance jumps over 25 Y,
  loop seam check (skip for non-looping films).
- Punctuated frame sampler for critics: per-frame motion from the MP4, pauses -> one held frame, moves -> mid
  frames tagged motion-only, first and last forced.
- Static-frame metric: 320x180 grey sampling, frame counted still when mean change is under about 0.35; flag any
  shot with stillness over 3 s or a settled hold under 30 frames before exit.
- Scale-empty metric: largest object height median per shot (flag under 110 px at 720p for more than 45 frames).
- Audio: window and envelope measurement per cue, `ebur128` loudness, cross-correlation to measure output offset.
- Typing-budget and reading-time audits computed from constants, not from greps of literals.

### 7.G Rendering defaults
- H.264 masters: `--crf=14-18` (lower for type-heavy), `--image-format=png` or `--jpeg-quality=100` when thin
  type or flat gradients matter, `--scale=2` for phone-sharp text or 4K from a 1080 layout; opaque background.
- Transparent overlays: ProRes 4444 + `yuva444p10le` + PNG frames, or VP8/VP9 WebM with alpha.
- Serial renders on laptops; `--concurrency=1` when diagnosing flicker; chunked multi-instance on servers.
- Keep `npm run typecheck` green before renders (hallucinated import paths fail deep inside a render).

### 7.H Decision table: which video type needs which techniques
| Type (frequently requested) | Structure that works | Key techniques | Community reference |
|---|---|---|---|
| Kinetic typography | beats of fixed length, cut between lines, one word per beat matters | Series of Sequences, punch 0.33->1 in 5 f, baseline pivot, words not letters | snapcn kinetic typography |
| Product launch / SaaS promo (15-45 s) | hook with product within 3 s, problem, 3-5 features as movements, proof, one CTA | real UI rebuilt from source, camera rig, cursor prop, word-locked VO or beat grid | agentic-product-demo, product-launch-motion, shotcraft, EveryInc |
| Feature loop for a web page | one flow start to finish, muted, loops | loop seam check, frame 0 poster, no sound dependence | agentic-product-demo |
| Explainer (2-8 min) | research -> narration -> storyboard -> chapters | word timestamps, chapter cards, one hero per shot, camera budget (about 3 moves per chapter), facts traced to sources | anything2explainer, claude-code-video-toolkit, OpenMontage |
| Data / chart video | one number per beat, chart drawn edge to edge | counters, racing bars, tabular nums, sourced data | RenderComp blog, remotion-dev GitHub Unwrapped |
| Map video | camera follows a smoothed route | turf, lerp camera, line progress | Remotion maps docs, Mapbox blog |
| 3D product | one hero shot | ThreeCanvas, frame-driven, tone-map before bloom | template-three, product-launch-motion |
| Shorts with captions | hook frame 0 composed, 2-4 word pages, loop back to frame 0 | createTikTokStyleCaptions, safe zones, no engagement-bait outro | hassancs91 make-short, template-tiktok |
| Talking-head recut / B-roll | cut first from transcript, then overlays | word-level transcript edits, captions avoiding the face, graphics in empty space | claude-youtube-editor, erduo, AIEV |
| Podcast audiogram | clip + waveform + captions | `visualizeAudio`, `useAudioData`, captions | template-audiogram |
| Logo sting (3-5 s) | mark in 0-0.8 s, wordmark 0.6-1.8 s, tagline 2-3.5 s, breathe, exit last 0.5 s | draw-on (`evolvePath`), mask reveal, flood from inside the mark (a logo cannot cover the frame by scaling: holes scale too) | haidrrrry, snapcn |
| Lyric / music video | music drives pacing | beat grid or RMS energy, per-line reveals between beats | HyperFrames music-to-video, shotcraft |

### 7.I Runtime decision table
| Situation | Choose |
|---|---|
| React team, data-driven or personalised at scale, Lambda/Cloud Run, Zod-typed props, existing Remotion skills (our case) | Remotion |
| A design-led HTML/GSAP piece, website-to-video, a registry block you want, or Apache-2.0 required | consider HyperFrames (learn its seek model; do not mix runtimes silently) |
| Hand-crafted vector explainer with a real-time editor, MIT required | Motion Canvas (or Revideo for headless pipelines) |
| Only trims/concats/burn-ins | FFmpeg directly |
| GSAP plugin-only effects inside a Remotion film | paused GSAP timeline seeked by frame (4.16) |
Community evidence is thin and partisan: HeyGen says agents produce more varied visuals in HTML/GSAP; a partisan
blog's timings (HyperFrames 7-10 s vs Remotion 16-20 s for 5 s renders) are unverified. Our lever is not the
runtime but the craft gates above, which port between runtimes.

### 7.J Community rules that are wrong or environment-specific (do not inherit)
- "`useVideoConfig().durationInFrames` returns the composition length inside a Sequence" (wrong now).
- "`Easing.out(Easing.cubic)` crashes, use only `Easing.bezier`" and "composition ids PascalCase only" (VidTSX).
- "Replace spring() with interpolate to avoid OOM" (unverified).
- "Always per-character stagger for headlines" (30x motion.md, haidrrrry) conflicts with kerning and reading
  arithmetic; use words or lines.
- "Idle elements always breathe / never hold still over 4 s" conflicts with "text dead still while read" and the
  heartbeat ban; use verb-driven motion, background drift at most, and one live element during holds.
- "Expo-out everywhere" conflicts with measured frame-clock freezes for small travel; check per-frame travel.
- "Five-layer stack with grain, grade and vignette on every scene" and "glow on the hero" are one house style; the
  opposite school bans glow entirely. Make texture a per-direction dial.
- Remotion licence prices and "BUSL" claims from comparison blogs; "HyperFrames has no Lambda" (it does).
- Studio-vs-render: getBoundingClientRect under Studio zoom needs `useCurrentScale()`; under camera transforms use
  layout metrics (`offsetWidth/offsetLeft`, integer-rounded `offsetTop`), or better, layout constants.

### 7.K Skill family hygiene
- Keep API knowledge separate from taste: the Liamrjohnston pattern (official `remotion-best-practices` for API
  correctness + small taste skills on top) avoids stale copies of official rules.
- This machine also has `ecc:remotion-video-creation` (a 29-rule copy of the older official rules) and the
  official `remotion-*` skills installed; our skill descriptions must route unambiguously so the right one loads.
- Budget agent context: one heavy task per sub-agent, shared primitives in the repo instead of in prompts, QA agents
  append findings as they go (anything2explainer lost a one-hour QA run that wrote nothing), dispatch parallel
  builders in waves because terminal/fork limits are machine-wide.
- No self-promotion or "star the repo" steps in delivery; no agent names in outputs.

---

## 8. Best examples to learn from

- https://github.com/AbubakrChan/product-launch-motion (references 01, 03, 04, 05, 06, 07, 10, 11): measured laws and 34 traps; includes a Remotion translation of a seek-based pipeline.
- https://github.com/snapcndev/snapcn/blob/main/.claude/skills/motion-quality/SKILL.md: the only sub-pixel measurements of text motion in the ecosystem.
- https://github.com/Zane-0x5a/remotion-director (docs/WHY.md, skills/critic-loop/CRITIC-PROTOCOL.md, design-brain references): blind critic, punctuated sampling, tempo pass, N draws.
- https://github.com/Vincentwei1021/video-shotcraft (references/aesthetic-rules.md, music-beat-sync.md, sound-design.md, gallery): case-law rules with the user feedback that created each rule; Apache-2.0.
- https://github.com/Alexwtlf/agentic-product-demo: nine motion rules, frame gate, render debugging order, title arithmetic.
- https://github.com/norahe0304-art/30x-video (cli/skill/rules): composition laws, evidence gates, honest disclosure, rhythmic vs non-rhythmic beat handling.
- https://github.com/crimeacs/product-demo-director (docs/EDITING.md, MOTION_GRAPHICS.md): story grammars for demos, judge-loop statistics, redaction rules.
- https://github.com/noamdorr/saas-product-demo-video (references): click positioning, beat sync inside Series, vertical porting, render/export defaults.
- https://github.com/Vincentwei1021/anything2explainer (reference/lessons.md, motion-vocabulary.md, composition-and-light.md): multi-agent explainer production lessons with numbers (PolyForm NC, read only).
- https://github.com/hassancs91/claude-faceless-shorts-creator (.claude/skills): shorts beat grammar with loop-to-frame-0 and SFX audibility calibration.
- https://github.com/Liamrjohnston/remotion-motion-graphics-skill: camera rig, reference-review gate, critic scoring rubric (all scores at least 8, average at least 8.5).
- https://github.com/degueba/onda (docs/motion-language.md, docs/remotion-capabilities.md): a motion token system and a USE/WRAP/SKIP map of Remotion packages.
- https://github.com/remotion-dev/remotion/issues/4300 and /4664: the best public research on render throughput.
- https://github.com/remotion-dev/remotion/discussions/3248, /6833, /5121, /5329: fuzzy edges, phone sharpness, video canvas compositing, Player performance.
- https://github.com/calesthio/OpenMontage (skills/meta/animation-runtime-selector.md, skills/core/remotion.md): runtime routing and a post-render verification protocol (AGPL, read only).

---

## 9. Open questions

1. Does the "expo-out freezes on a frame clock" measurement (snapcn, 50 px rise) hold for larger travel and for
   60 fps? Our skills need a rule of thumb (minimum per-frame travel) rather than a banned curve.
2. Is `will-change` in renders harmful (snapcn: stale rasters across tabs) or helpful (issue #11428 Lambda strips)?
   Needs a local A/B on 4.0.528 with `--concurrency` above 1 and on Lambda.
3. What is the real audio offset of a 4.0.528 server render (AAC, 48 kHz, MP4)? Issue #7099 concerns the web
   renderer's container duration; shotcraft measured about 1.28 f on its own pipeline and once 4 f. Measure with
   cross-correlation before hard-coding any compensation.
4. Are the `@remotion/media <Video>` hangs (#10701 Windows ANGLE, #10909 Docker memory) fixed in 4.0.528? Until
   verified, should our default for footage stay `<OffthreadVideo>`?
5. Does the spring OOM claim reproduce with dozens of distinct spring configs over 1,200+ frames?
6. Multi-instance chunked rendering vs a single `renderMedia` on this Mac Studio (M-series, 36 GB): what split
   gives the best wall time for type-heavy vs footage-heavy compositions?
7. Which loudness target should we standardise per platform (-14 LUFS vs -16 LUFS), and should the master step be
   a skill script?
8. Is a blind critic built from Claude sub-agents as effective as remotion-director reports, and what frame budget
   per round keeps cost acceptable?
9. HyperFrames claims more visual variety from agents; is that a property of the runtime or of its skills? A
   same-brief bake-off on this machine would settle whether any HTML/GSAP ideas should be ported into our
   Remotion skills.

---

## Ranked list: the 25 most useful external resources

1. AbubakrChan/product-launch-motion, references 01-11 (MIT). Measured motion grammar, camera, cursor, grade,
   sound arithmetic, 34 traps. https://github.com/AbubakrChan/product-launch-motion
2. snapcn motion-quality skill and anti-patterns (MIT). Text judder physics, easing freeze, transitions.
   https://github.com/snapcndev/snapcn/blob/main/.claude/skills/motion-quality/SKILL.md
3. Zane-0x5a/remotion-director, WHY + critic protocol + design-brain (MIT). How to get taste out of a model and
   judge it honestly. https://github.com/Zane-0x5a/remotion-director
4. Vincentwei1021/video-shotcraft rules, beat sync, sound design, shot cards (Apache-2.0).
   https://github.com/Vincentwei1021/video-shotcraft
5. Alexwtlf/agentic-product-demo README and product-demo skill (MIT per README).
   https://github.com/Alexwtlf/agentic-product-demo
6. norahe0304-art/30x-video rules (MIT). Composition laws, QC gates, disclosure, narration sync.
   https://github.com/norahe0304-art/30x-video
7. crimeacs/product-demo-director EDITING + MOTION_GRAPHICS (MIT). Demo story grammars, judge-loop statistics.
   https://github.com/crimeacs/product-demo-director
8. noamdorr/saas-product-demo-video references (MIT). Click positioning, beat sync, vertical port, render export.
   https://github.com/noamdorr/saas-product-demo-video
9. Remotion issues #4300 and #4664 (render throughput research).
   https://github.com/remotion-dev/remotion/issues/4300
10. Vincentwei1021/anything2explainer reference files (PolyForm NC, read only). Multi-agent long-form lessons.
    https://github.com/Vincentwei1021/anything2explainer
11. hassancs91/claude-faceless-shorts-creator skills (MIT). Shorts grammar, SFX calibration.
    https://github.com/hassancs91/claude-faceless-shorts-creator
12. Liamrjohnston/remotion-motion-graphics-skill (MIT). Camera rig, critic rubric, reference gate.
    https://github.com/Liamrjohnston/remotion-motion-graphics-skill
13. Remotion Discussions #3248, #6833, #5121, #5329 (render sharpness, compositing, Player perf).
    https://github.com/remotion-dev/remotion/discussions/6833
14. degueba/onda motion language + Remotion capabilities map (MIT). https://github.com/degueba/onda
15. HyperFrames README and "HyperFrames or Remotion?" guide (Apache-2.0).
    https://hyperframes.heygen.com/guides/hyperframes-vs-remotion
16. iart-ai/motion-design-skills (MIT). Animation principles, easing library, shot composition, colour, AE
    expressions. https://github.com/iart-ai/motion-design-skills
17. OpenMontage runtime selector, Remotion skill, HyperFrames skill (AGPL, read only).
    https://github.com/calesthio/OpenMontage
18. WWDC23 "Animate with springs" notes and the duration/bounce formulas.
    https://wwdcnotes.com/documentation/wwdc23-10158-animate-with-springs/ and https://www.kvin.me/posts/effortless-ui-spring-animations
19. Material 3 motion tokens (source values).
    https://github.com/material-components/material-web/blob/main/tokens/versions/latest/sass/_md-sys-motion.scss
20. snapcn articles: kinetic typography, TikTok captions, Remotion vs Motion Canvas.
    https://snapcn.dev/remotion-kinetic-typography
21. Netflix Timed Text Style Guide (reading speed, line length, event duration).
    https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide
22. RenderComp data-visualisation guide (counters, bars, racing charts).
    https://rendercomp.com/blog/data-visualization-animations-remotion-bar-charts-counters/
23. Mapbox "cinematic route animations" (camera follow, lerp smoothing, line progress).
    https://www.mapbox.com/blog/building-cinematic-route-animations-with-mapboxgl
24. haidrrrry/claude-remotion-skill motion patterns and design rules (MIT; use with the caveats in 7.J).
    https://github.com/haidrrrry/claude-remotion-skill
25. Component registries for reuse: RemotionUI, remocn, remotion-bits (MCP find/fetch), ali-abassi template
    catalog. https://github.com/riaz37/remotion-ui
