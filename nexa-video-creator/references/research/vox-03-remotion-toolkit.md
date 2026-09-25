# 03 · Remotion toolkit for a Vox-style explainer look

Research date: 2026-09-25. Every URL below was accessed on 2026-09-25.

Target: the `nexa-video-creator` renderer (Remotion **4.0.528**, React 19.2.3; its template currently depends only on `@remotion/cli`, `@remotion/google-fonts` and `@remotion/media`, all pinned to 4.0.528). The sibling project `nexa-media/remotion-broll` already has `@remotion/paths`, `shapes`, `noise`, `rough-notation`, `layout-utils`, `transitions` at 4.0.528, which I used to confirm exports.

Machine: Mac Studio, Apple M4 Max, 14 CPU threads, 36 GB, macOS 26.6.1, Node 26.7.0, ffmpeg 8.1.1, swiftc 6.3.3, `uv` and Python 3.12 available (system `python3` is 3.9.6, too old for current rembg; use a uv venv).

Method: Remotion docs fetched as Markdown (`<url>.md`), GitHub REST API via `gh` (stars, licence, last push, file trees), the npm registry (`npm view`), the locally installed official skills in `~/.claude/skills/remotion-*` (version-stamped 4.0.528), and the extracted `@remotion/effects@4.0.528` tarball (shader and backend inspection).

Version note: Remotion 4.0.528 was published 2026-09-24 and 4.0.529 on 2026-09-25. Every `remotion` and `@remotion/*` package must stay on exactly the same version; install extras with `npx remotion add <pkg>`, which pins them. All packages named below exist at 4.0.528.

---

## 0. Recommendations at a glance

| # | Item | Decision | Why (licence, determinism, performance) |
|---|---|---|---|
| 1 | Official agent skills `remotion-dev/skills` (local copy in `~/.claude/skills`, stamped 4.0.528) | **Adopt** | Rules match our exact version (effects, highlights, transitions, maps render stability). Update only through `npx remotion upgrade`. The repo has no LICENSE file: use it, do not paste its text into our public MIT repo. |
| 2 | `@remotion/transitions`: `TransitionSeries`, `TransitionSeries.Overlay`, CSS presentations (`fade`, `slide`, `wipe`, `iris`, `clockWipe`, `pushCut`, `flip`), custom presentations | **Adopt** | Deterministic, cheap. The HTML-in-canvas presentations (`bookFlip`, `filmBurn`, `crosswarp`, `dissolve`, `ripple`, `zoomBlur`, `dreamyZoom`...) are WebGL: hero moments only. |
| 3 | `@remotion/paths` (`evolvePath`, `getSubpaths`, `getLength`, `getPointAtLength`, `getTangentAtLength`, `interpolatePath`, `warpPath`, `cutPath`) | **Adopt** | MIT. Draw-on borders, routes, arrows, chart lines. |
| 4 | `@remotion/shapes` incl. `<Callout>` (4.0.477+), `Arrow`, `Spark`, `Pie` | **Adopt** | MIT. `<Callout>` is a ready speech bubble path generator; shapes accept `effects`. |
| 5 | `@remotion/rough-notation` (4.0.490+): `Highlight`, `Underline`, `Circle`, `Box`, `Bracket`, `StrikeThrough`, `CrossedOff`, with a `seed` prop | **Adopt** | MIT, built on roughjs 4.6.6. Document and newspaper highlights, driven by `progress`. |
| 6 | `@remotion/layout-utils` (`fitText`, `fitTextOnNLines`, `measureText`, `fillTextBox`) | **Adopt** | MIT. Headline fitting for data-driven scenes. |
| 7 | `@remotion/noise` (`noise2D/3D/4D(seed, ...)`) | **Adopt** | MIT, seeded. Idle drift, wobble, jitter. |
| 8 | `@remotion/google-fonts` | **Adopt** | Typewriter (Special Elite, Courier Prime), newsprint (Old Standard TT, Libre Caslon Text, Source Serif 4), marker (Permanent Marker, Caveat), Bangla (Tiro Bangla, Noto Serif/Sans Bengali, Hind Siliguri, Anek Bangla, Baloo Da 2): all present in 4.0.528. |
| 9 | `@remotion/media` `<Video>` for alpha overlays (VP9 alpha WebM) | **Adopt** | Decodes alpha (CPU path since 4.0.482); local renders are clean. ProRes input needs the optional `@mediabunny/prores` (MPL-2.0). |
| 10 | `@remotion/effects`, used selectively: `paper()`, `noise()` to bake plates; `halftone()`, `outline()`, `roughenEdges()`, `tear()`, `duotone()`, `grayscale()`, `levels()` for hero shots | **Adopt (bounded)** | Exactly the Vox vocabulary, deterministic via `seed`. But 63 of the 73 effect modules are WebGL2 (need `--gl=angle`), each effected component owns canvases, and Chrome caps a page at about 16 live WebGL contexts. Remotion License (npm says `UNLICENSED`). |
| 11 | SVG maps: `d3-geo` 3.1.1 + `topojson-client` 3.1.0 + Natural Earth 5.1.2 (public domain, with point-of-view variants incl. Bangladesh, India, Pakistan, China) or `world-atlas` 2.0.2 for quick world maps | **Adopt** | ISC and public domain. No WebGL, no tiles, crisp at any zoom, trivially deterministic. |
| 12 | `d3-scale` 4.0.2 + `d3-shape` 3.2.0 | **Adopt** | ISC. Scales and path generators only; render as JSX and animate with `interpolate`/`evolvePath`, never `d3-transition`. |
| 13 | `perfect-freehand` 1.2.3 | **Adopt** | MIT, deterministic for identical input. Tapered marker strokes. |
| 14 | Apple Vision `VNGenerateForegroundInstanceMaskRequest` (macOS 14+) through a ~15-line Swift CLI; `VNRecognizeTextRequest` for OCR boxes | **Adopt (write the CLI)** | Local, fast, no model licence question. Same model as Finder's "Remove Background". |
| 15 | `rembg` 2.0.85 only with `-m birefnet-general` (MIT) or `isnet-general-use` / `u2net` (Apache-2.0) | **Adopt as fallback** | Since v2.0.80 (2026-08-17) the **default** model is `bria-rmbg` (RMBG-2.0), which needs a paid BRIA agreement for commercial use. |
| 16 | CC0 / public-domain sources: ambientCG and Poly Haven (textures), Smithsonian Open Access and The Met Open Access (CC0 images), US federal works, Natural Earth | **Adopt** | Safe to commit into the public skills repo. |
| 17 | LottieFiles free animations through `@remotion/lottie` | **Adopt** | Lottie Simple License allows commercial use without attribution. Good for flat, stylised flames and sparks that match paper collage. |
| 18 | Depth Anything V2 **Small** (Apache-2.0, Apple Core ML build exists) | **Adopt for 2.5D photos** | Depth maps for photo push-ins. |
| 19 | Asset baker (Python 3.12 via `uv`, Pillow + numpy; or Node + `sharp` Apache-2.0): halftone dots, red marker backing, white sticker edge, baked shadow, crop to alpha, size caps | **Write ourselves** | Moves all per-pixel work out of the render; each layer becomes a plain `<Img>` with transforms. |
| 20 | Plates: locked paper background (bake `paper()` once with `npx remotion still`, or a CC0 scan) and 8 grain frames | **Write ourselves** | Near-zero per-frame cost, identical every build. |
| 21 | `CollageCamera` + layer verbs (slide, pop, place, peel, stamp, drift) with depth parallax and push-ins | **Write ourselves** | The core of the look; about 150 lines; the MIT collage kit in `hassancs91/claude-faceless-shorts-creator` is a useful reference. |
| 22 | Map kit (SVG): projection presets, precomputed path JSON, per-subpath border draw, great-circle routes, label chips at pole of inaccessibility (`polylabel`, ISC), fill reveals, faux extrusion | **Write ourselves** | Nothing off the shelf matches a paper map; the pieces are small. |
| 23 | Chart and counter kit, PriceTag, Typewriter (grapheme-safe for Bangla), SpeechBubble, Newspaper/Document mock-ups | **Write ourselves** | Small components on top of #3 to #8 and #12. Remotion Elements (Data, Text, Storytelling) are good references. |
| 24 | Burn effect as a `createEffect()` WebGL2 shader (noise threshold, ember rim, char band) plus seeded ember sprites | **Write ourselves** | Deterministic, about 60 lines; no Shadertoy code. |
| 25 | Paper transitions: paper-sheet `Overlay` wipe and a torn-edge slide-over custom presentation; `tear()` inside `<HtmlInCanvas>` as a hero option | **Write ourselves** | CSS versions are cheap and stable; `HtmlInCanvas` is an unstable Chrome API. |
| 26 | `rembg` default model, BRIA RMBG-1.4/2.0 | **Avoid** | Commercial use needs a paid BRIA agreement. |
| 27 | Depth Anything V2 Base/Large/Giant; DepthFlow and parallax-maker inside our tools | **Avoid** | CC BY-NC 4.0; AGPL-3.0. |
| 28 | Shadertoy code | **Avoid** | Default licence is CC BY-NC-SA 3.0. Use MIT gl-transitions or write our own. |
| 29 | ProductionCrate / FootageCrate assets in the automated pipeline | **Avoid** | Their terms forbid use in "automated content generation" systems, with US$5,000 per element damages. |
| 30 | Texturelabs and other no-redistribution assets inside the public MIT skills repo | **Avoid** | Fine inside a client project folder, never committed to the public repo. |
| 31 | Code from repos without a licence file (Anil-matcha, Cliff007007, niovideoshelp, sxhzju, reactvideoeditor, ali-abassi) and from `anything2explainer` (PolyForm Noncommercial) | **Avoid** | Read for ideas only. |
| 32 | Per-frame CSS `filter: drop-shadow()`/`blur()` chains, `box-shadow`, big gradients on many layers; full-frame `feTurbulence` every frame | **Avoid** | Listed as slow by Remotion; SVG filters take Chrome's CPU path. Bake instead. |
| 33 | More than ~16 WebGL effect canvases mounted at once (premounted scenes count) | **Avoid** | Chrome drops the oldest context. |
| 34 | Live MapLibre/MapTiler camera per frame for the paper-map look | **Avoid** | Official skill: shimmer, needs a fixed plate and `--concurrency=1`. Keep MapLibre for real basemaps only. |
| 35 | `Math.random`, CSS animations/transitions, `d3-transition`, R3F `useFrame`, Lottie autoplay, stepped physics | **Avoid** | Breaks out-of-order parallel rendering. |
| 36 | Paid AI-video "Vox" pipelines (Atlas Cloud, MaxFusion, Seedance) as the main engine | **Avoid** | Per-clip cost, no frame determinism, text not editable. |
| 37 | `@remotion/animated-emoji` (needs CC BY 4.0 credit) and meme clips in `@remotion/sfx` for client work | **Avoid unless credited/cleared** | Attribution and third-party rights. |
| 38 | `tear()` on a whole scene; WebGL context budget; `halftone()` vs baked look | **Spike first (1 day)** | Measure ms/frame, memory over a 3-minute render with `--gl=angle`, and context loss. |

Licence of Remotion itself: free for individuals and for-profit companies with up to 3 employees. Above that a Company License is required: "Remotion for Automators" is $0.01 per render with a $100/month minimum (this is our case: automated client videos), "Remotion for Creators" is $25/month per seat. Confirm NexaLance's head count before the first client delivery.

---

## 1. Remotion's own resources

### 1.1 Official agent skills (`remotion-dev/skills`)

Repo: https://github.com/remotion-dev/skills. 4,709 stars, last push 2026-09-25 (HEAD tracks 4.0.529 and adds `remotion-markup/motion-blur.md`), no LICENSE file. Installed with `npx skills add remotion-dev/skills`; `npx remotion upgrade` updates project-local copies. The local copy in `~/.claude/skills/` is stamped `version: 4.0.528`.

| Skill | What its rules teach (rule files) |
|---|---|
| `remotion-best-practices` | Router: loads the others; "preserve user changes made outside the conversation". Bundles every other skill as `*/REFERENCE.md`. |
| `remotion-create` | Scaffold with `npx create-video@latest --yes --blank --no-tailwind`; `video-layout.md`: design for one focal point, safe area 80 px sides and 100 px top/bottom at 1080 px wide, headline at least 84 px, supporting text at least 44 px; `tailwind.md`. |
| `remotion-markup` | Animate only with `useCurrentFrame()` + `interpolate()`; no CSS transitions, CSS animations or Tailwind animation classes; `Easing.bezier()` / `Easing.spring()`; keep `interpolate()` inline in `style`; use the `scale`, `translate`, `rotate` properties instead of `transform`; `output: 'perceptual-scale'` for scale; images through `<CanvasImage>`/`<Img>`, animated images through `<AnimatedImage>`; `from`, `durationInFrames`, `trimBefore` on components; always `premountFor` sequences. Rule files: `3d`, `audio`, `audio-visualization`, `calculate-metadata`, `compositions`, `connected-compositions`, `cropping`, `effects` (effect list + `createEffect()` template for 2D and WebGL2), `embedding-videos`, `ffmpeg`, `gifs`, `google-fonts`, `html-in-canvas`, `images`, `light-leaks`, `local-fonts`, `lottie`, `measuring-dom-nodes`, `measuring-text`, `multi-scene-video` (one file per scene, connected compositions, `TransitionSeries`), `parameters` (Zod), `sequencing`, `sfx`, `silence-detection`, `text-highlights` (rough-notation), `timing` (including `posterize` for stepped motion), `transitions` (transitions vs overlays, duration maths), `video-editing`, `voiceover`. |
| `remotion-maps` | Pick exactly one technique: `static-map` (image plate + overlays, the most deterministic), `mapbox` (key), `maplibre` (free, Turf routes, `interactive:false`, `fadeDuration:0`, `preserveDrawingBuffer`, wait for `idle`, `--gl=angle --concurrency=1`), `maptiler` (annotations on real geography; custom GeoJSON with `prep-geo.mjs`, labels at the pole of inaccessibility, per-country trigger timing), `cesium` (3D flythroughs). `render-stability.md`: per-frame `jumpTo()` shimmers; render one oversized fixed plate (max 4096 px) and move it with CSS. |
| `remotion-render` | `npx remotion render`, `still`, `--frames=0,30,90` spot checks; `transparent-videos.md`: ProRes 4444 (`yuva444p10le`) for editors, VP9 `yuva420p` WebM for browsers. |
| `remotion-interactivity` | `Interactive.*` elements, named layers, hardcoded inline styles and keyframes so Studio can edit them; effects arrays inline. Optional for our compiled, data-driven scenes. |
| `remotion-captions` | `Caption` JSON type; transcribe, display, import SRT. |
| `remotion-docs` | Algolia search, then fetch `<docs-url>.md`. |
| `remotion-multimedia` | Mediabunny: media duration and dimensions. |
| `remotion-saas` | Player, templates, Lambda/Vercel/Cloudflare rendering. |
| `remotion-studio` | `npx remotion studio --no-open` and flags. |
| `remotion-upgrade` | `npx remotion upgrade`, align auxiliary packages, update skills. |

Most relevant for this look: `remotion-markup/effects.md`, `text-highlights.md`, `transitions.md`, `timing.md`, `measuring-text.md`, `html-in-canvas.md`, and the maps `render-stability.md` plus the MapTiler custom-GeoJSON architecture (timing model, per-country triggers, pole-of-inaccessibility labels).

Older forks (for example `vercel-labs/json-render/skills/remotion-best-practices/rules/charts.md`) still carry the pre-restructure `charts.md` and `text-animations.md`; the current equivalents live in the Prompt to Motion Graphics SaaS template (section 1.5).

### 1.2 Packages at 4.0.528

| Package | npm licence | Use for this look | Notes |
|---|---|---|---|
| `remotion` | Remotion License | `interpolate`, `Easing.spring` (4.0.476+), `random()`, `<Img>` (effects 4.0.469+, `premountFor` 4.0.497+), `<CanvasImage>` (4.0.466+), `<Solid>` (4.0.464+), `<HtmlInCanvas>` (4.0.455+), `createEffect()` | 4.0.528 adds `premountFor` to many components. |
| `@remotion/effects` | UNLICENSED (Remotion License) | paper, grain, halftone, outline, tear, duotone | See 1.3. Needs `Config.setChromiumOpenGlRenderer('angle')` for WebGL2 effects. |
| `@remotion/transitions` | UNLICENSED (Remotion License) | scene transitions, overlays, custom presentations | Depends on `@remotion/paths`, `@remotion/shapes`. |
| `@remotion/paths` | MIT | draw-on lines | Exports verified: `evolvePath, getLength, getPointAtLength, getTangentAtLength, getSubpaths, interpolatePath, warpPath, cutPath, centerPath, scalePath, translatePath, reversePath, normalizePath, parsePath, getBoundingBox`. |
| `@remotion/shapes` | MIT | speech bubbles, arrows, pies | Components: `Arrow, Callout, Circle, Ellipse, Heart, Pie, Polygon, Rect, Spark, Star, Triangle` plus `make*()` path functions. `makeCallout({width, height, pointerLength, pointerBaseWidth, pointerPosition, pointerDirection, edgeRoundness, cornerRadius})`. |
| `@remotion/rough-notation` | MIT | highlights, circles, brackets | Props: `progress`, `seed`, `color`, `strokeWidth`, `iterations`, `padding`, `roughness`, `bowing`, `rtl`. |
| `@remotion/layout-utils` | MIT | text fitting | Measure only after fonts load. |
| `@remotion/noise` | MIT | seeded noise | Wraps `simplex-noise` 4.0.1. |
| `@remotion/google-fonts` | Remotion License (fonts OFL/Apache) | typography | `loadFont('normal', {weights, subsets})`; 1,835 families. |
| `@remotion/media` | not stated (monorepo Remotion License applies) | `<Video>`, `<Audio>` | Mediabunny 1.56.1; falls back to `<OffthreadVideo>` for unsupported codecs. |
| `@remotion/lottie` | Remotion License | vector flames, icons | Peer `lottie-web ^5` (5.13.0, MIT). |
| `@remotion/three` | MIT | 3D extrusion, depth-displaced photo planes | Peers `three >=0.137`, `@react-three/fiber >=8` (9.8.1 works with React 19). `<ThreeCanvas width height>` required; `useFrame` forbidden. |
| `@remotion/rive` | Remotion License | optional | Bundles `@rive-app/canvas-advanced` 2.31.5 (MIT). `<RemotionRiveCanvas>` accepts effects. |
| `@remotion/gif` | Remotion License | legacy GIFs | Core `<AnimatedImage>` now covers GIF, APNG, WebP, AVIF in Chrome. |
| `@remotion/animated-emoji` | MIT (package) | avoid for client work | Noto animated emoji are CC BY 4.0 (attribution). |
| `@remotion/motion-blur` | MIT | `Trail`, `CameraMotionBlur` | Renders N copies of the layer; costly. |
| `@remotion/gsap` | MIT | only if a scene must be authored in GSAP | Exists since 4.0.517. |
| `@remotion/sfx` | MIT (package) | whoosh, page-turn, shutter | Each sound has its own licence page; several are meme clips. |
| `@remotion/svg-3d-engine` | none stated | avoid | Undocumented internal "3D SVG extrusion". |

### 1.3 `@remotion/effects`: the parts that matter here

Supported targets: `<Solid>`, `<HtmlInCanvas>`, `<Video>`, `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Gif>`, `<RemotionRiveCanvas>`, and `@remotion/shapes` components. Effects chain in array order. Backends (from the 4.0.528 tarball, 73 effect modules): 2D canvas for `brightness, contrast, grayscale, hue, invert, saturation, scale, tile, tint, translate`; WebGL2 for the other 63.

| Effect | Since | Key params | Vox use |
|---|---|---|---|
| `paper()` | 4.0.486 | `colorFront, colorBack, contrast, roughness, fiber, fiberSize, crumples, crumpleSize, folds, foldCount, drops, fade, seed, scale` | Bake the locked paper plate once. The official "Paper Texture" element animates the seed (posterized) for a boiling-paper look; we want a fixed seed. |
| `noise()` | 4.0.469 | `amount, seed, premultiply` | Grain on a full-frame `<Solid>`; pass a frame-derived seed to animate. |
| `halftone()` | 4.0.467 | `shape (circle/square/line), dotSize, dotSpacing, rotation, offsetX/Y, sampling, colorMode (solid/source), dotColor, invert` | B&W photo cutouts. Shader detail: transparent pixels count as white, so they get no dots; the output is dots on transparency, so place a paper-white silhouette underneath for a newsprint look. Dot radius is linear in darkness; pre-adjust with `levels()`. |
| `outline()` | 4.0.515 | `width, edgeSimplification, color, opacity, outlineOnly` | White sticker edge on cutouts; with `outlineOnly: true` a filled grown silhouette, usable as the red backing blob. |
| `roughenEdges()` | 4.0.487 | `amount, border, scale, seed` | Ragged torn-paper or marker edges on any alpha. |
| `tear()` | 4.0.523 | `progress, angle, rotation, jaggedness` | Rip a layer or, inside `<HtmlInCanvas>`, a whole scene. |
| `duotone()` | n/a | `darkColor, lightColor, threshold` | Two-colour archival treatment. |
| `grayscale()`, `levels()` | 4.0.466 / n/a | `amount`; `blackPoint, whitePoint, gamma` | Pre-conditioning for halftone. |
| `dropShadow()`, `glow()` | n/a | WebGL2 | GPU shadows when a shadow must animate. |
| `speckle()`, `burlap()` | n/a | `density, size, randomness`; `amount, size, roughness, seed, color` | Print wear, fibre. |
| `noiseDisplacement()` | 4.0.474 | `center, radius, strength, seed, grainSize, passes, feather` | Heat haze above the burning note. |
| `waves()`, `lines()` | n/a | colours, direction, thickness, gap, rotation, animatable `offset`, wave amplitude/period | Hatched animated water inside ocean shapes. |
| `evolve()`, `pixelDissolve()` | n/a | `progress, direction, feather`; `progress, columns, rows, seed, feather` | Soft directional reveals. |
| `lightLeak()` | 4.0.500+ | `progress, seed, hueShift` | Warm overlay at cuts. |

Custom effects: `createEffect({type, label, documentationLink, backend: '2d' or 'webgl2' or 'webgpu', calculateKey, setup, apply, cleanup, schema, validateParams})`. The `remotion-markup/effects.md` rule contains a complete 2D and WebGL2 template. `calculateKey` must include every parameter that changes output.

### 1.4 Transitions and custom presentations

At 4.0.528 the presentations are:

- CSS based (cheap, any renderer): `fade`, `slide`, `wipe`, `flip`, `clockWipe`, `iris`, `pushCut`, `none`.
- HTML-in-canvas + WebGL (gl-transitions ports, MIT): `blurSlide`, `bookFlip`, `crossZoom`, `crosswarp`, `dissolve`, `dreamyZoom`, `filmBurn`, `linearBlur`, `ripple`, `swap`, `zoomBlur`, `zoomInOut`.

`<HtmlInCanvas>` needs Chrome 149+ with a flag; Remotion ships its own compiled Chrome with the flag on, so `npx remotion render` works, but the docs call the API unstable, nesting is unsupported, and WebGL needs `--gl=angle`. A custom presentation is a component receiving `children`, `presentationDirection` (`entering`/`exiting`), `presentationProgress` (0 to 1), `presentationDurationInFrames` and `passedProps`, and must be a pure function of those. `makeHtmlInCanvasPresentation(shader)` turns a GLSL `HtmlInCanvasShader` (for example an MIT gl-transitions shader) into a presentation. `TransitionSeries.Overlay` plays an effect over a cut without shortening the timeline.

### 1.5 Templates, Elements, Prompts, Showcase

- Templates (https://www.remotion.dev/templates): Blank, Hello World, Next.js, Recorder, Prompt to Motion Graphics SaaS, Render Server, Electron, React Router 7, 3D, Stills, Audiogram, Music Visualization, Prompt to Video, Skia, Overlay, Code Hike, Stargazer, TikTok; paid: Editor Starter ($600), Timeline ($300), Watercolor Map. The Prompt to Motion Graphics template ships agent rules in `src/skills/`: `charts.md` (stagger bars 3 to 5 frames, always label the y axis, value labels inside bars), `typography.md` (typewriter by string slicing, never per-character opacity; smooth caret blink), `messaging.md` (chat bubbles), plus `3d`, `sequencing`, `spring-physics`, `transitions`, `social-media`.
- Elements (https://www.remotion.dev/elements): copy-paste components whose source lives in the monorepo under `packages/docs/elements/` (treat as Remotion-licensed reference code; do not paste into our MIT repo). Relevant: Data (Horizontal/Vertical Bar Chart, Line Chart, Pie Chart, Number Counter with `tabular-nums`), Maps (A-to-B Map Flyover on MapLibre + Turf, Watercolor Map on Stamen watercolor tiles hosted by Cooper Hewitt, CC BY 3.0 + OpenStreetMap attribution), Text (Text Marker, Circle Marker, Crossed Off, Strike Through, News Article Highlight built on `<Highlight>`), Storytelling (On-Screen Messages, Polaroid Pictures), Backgrounds (Paper Texture, Notebook Paper, Moving Waves), Commerce (Tear, built as `<HtmlInCanvas effects={[scale(), tear()]}>`).
- Prompts gallery (https://www.remotion.dev/prompts): "News article headline highlight" (Tesseract OCR finds text boxes on a screenshot, rough.js highlighter evolves left to right, slight 3D rotation), "Bar + Line Chart (combined)", "Travel Route on Map with 3D landmarks".
- Showcase (source: `packages/docs/src/data/showcase-videos.tsx`): data and map pieces (Electricity Maps, Coronavirus Cases Visualization, MUX stats with source code, Transfer Fee Record), no paper-collage explainer.
- Remotion Pro store (https://www.remotion.pro/store): Editor Starter $600, Timeline $300, Cube Transition $10, Colors and Shapes $20. Nothing we need.

---

## 2. GitHub projects and skills

Stars and last push from the GitHub API on 2026-09-25.

| Project | Stars | Last push | Licence | Deterministic Remotion? | What is reusable |
|---|---|---|---|---|---|
| [hassancs91/claude-faceless-shorts-creator](https://github.com/hassancs91/claude-faceless-shorts-creator) | 263 | 2026-08-18 | MIT | Yes | `remotion/src/lib/collage.tsx`: `CollageBoard` camera with keyframed x/y/zoom and per-layer depth parallax, `Layer` entrance verbs (pop, place with overshoot, slide, rise, wipe), `Cutout` with sticker edge, `PaperBG`, `ArchivalPhoto`, `LabelChip`, `MarkerHighlight`, `SketchArrow`; `vox-shorts/DESIGN.md` (paper world, choreography over animation, camera as narrator, contrast rule: cream strips behind words over busy layers). Caveats: sticker edge and shadow are chains of CSS `drop-shadow()` (slow at scale); `tools/cutout.py` calls `rembg.remove()` with no model, which on rembg 2.0.80+ means non-commercial `bria-rmbg`. |
| [Phantomlau3674/voxstylehub-steven](https://github.com/Phantomlau3674/voxstylehub-steven) | 24 | 2026-07-22 | MIT | Yes (Remotion optional) | QA ideas worth copying: block "caption-only-static" stretches (only captions change), phone-downsample check for tiny subjects, a transition contract naming the inherited anchor (material, object, rail, aperture, colour field, motion). Paper-native motion verbs: slide, reveal, peel, pivot, stamp, drop, trace, wipe. |
| [Calm-Rock/map-trip-video](https://github.com/Calm-Rock/map-trip-video) | 0 | 2026-09-24 | MIT | Yes | d3-geo + world-atlas + `geoInterpolate` great-circle route in SVG, seeded star field, ANGLE config for a three.js scene. |
| [zcreativelabs/react-simple-maps](https://github.com/zcreativelabs/react-simple-maps) | 3,362 | 2026-09-12 | MIT | Yes if props come from the frame | Declarative d3-geo wrapper; direct d3-geo is simpler for us. |
| [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | 195 | 2026-08-12 | MIT | Yes | Render, inspect frames, fix loop; grain/grade/Ken Burns patterns. |
| [tmoody1973/pasteup](https://github.com/tmoody1973/pasteup) | 3 | 2026-07-07 | MIT | Own Python compositor | Halftone paper-collage stop-motion "on twos" with wobble, enter paths and spins; ideas only. |
| [iart-ai/motion-design-skills](https://github.com/iart-ai/motion-design-skills) | 33 | 2026-06-22 | MIT | Partly | Motion fundamentals. |
| [remotion-dev/template-prompt-to-motion-graphics-saas](https://github.com/remotion-dev/template-prompt-to-motion-graphics-saas) | 258 | 2026-09-09 | no file | Yes | `src/skills/charts.md`, `typography.md`, `messaging.md`. |
| [remotion-dev/typewriter](https://github.com/remotion-dev/typewriter) | 38 | 2024-02-26 | no file | Yes | Basic typewriter. |
| [remotion-dev/mapbox-example](https://github.com/remotion-dev/mapbox-example) | 38 | 2026-01-24 | no file | Yes (Mapbox key) | Route on Mapbox. |
| [stroniarz/remove-bg](https://github.com/stroniarz/remove-bg) | 1 | 2026-04-29 | MIT | n/a | 70-line Swift Vision CLI plus a Claude Code SKILL.md. |
| [Alisa0808/vox-director](https://github.com/Alisa0808/vox-director) | 2,031 | 2026-08-11 | MIT | No (AI video via Atlas Cloud + ffmpeg) | `references/beat-layer.md` (14 narrative arcs, hook and pacing), prompt vocabulary and 9 theme presets, `local-engine.md` (cut a poster into parts and animate frame by frame). |
| [CK42BB/vox-explainer-skill](https://github.com/CK42BB/vox-explainer-skill) | 109 | 2026-07-11 | MIT | No (AI video) | Voice-over-first timing (measured VO is the master clock), style anchor frame. |
| [Anil-matcha/vox-ai-motion-graphics-generator](https://github.com/Anil-matcha/vox-ai-motion-graphics-generator) | 222 | 2026-09-02 | no file (README badge claims MIT) | No | Ideas only until a LICENSE file exists. |
| [Vincentwei1021/anything2explainer](https://github.com/Vincentwei1021/anything2explainer) | 2,058 | 2026-09-18 | PolyForm Noncommercial 1.0.0 | Yes (black-canvas style) | Do not reuse code; ideas: research-to-storyboard flow, per-shot agents, quantitative frame QC. |
| [Cliff007007/paper-collage-video](https://github.com/Cliff007007/paper-collage-video) | 41 | 2026-08-02 | no file | Partly | Gate flow; ideas only. |
| [niovideoshelp-jpg/documentary-remotion](https://github.com/niovideoshelp-jpg/documentary-remotion) | 0 | 2026-09-24 | no file | Yes | Paper, photography, texture, radar and geography components; country reveal with projected boundaries as SVG clip plus "liquid fill"; `ASSETS.md` provenance practice. Ideas only. |
| [sxhzju/motion-remotion-08-collage-20260924](https://github.com/sxhzju/motion-remotion-08-collage-20260924) | 0 | 2026-09-24 | no file | Yes | Procedural paper texture; ships third-party reference crops. Avoid. |
| [reactvideoeditor/remotion-templates](https://github.com/reactvideoeditor/remotion-templates) | 247 | 2026-04-21 | no file | Yes | Chart templates; ideas only. |
| [ali-abassi/remotion-templates](https://github.com/ali-abassi/remotion-templates) | 27 | 2026-08-23 | no file | Yes | Ideas only. |
| [wilwaldon/Claude-Code-Video-Toolkit](https://github.com/wilwaldon/Claude-Code-Video-Toolkit) | 84 | 2026-02-26 | no file | n/a | Link index. |
| [itsjwill/vanta](https://github.com/itsjwill/vanta) | 122 | 2026-07-26 | unclear (NOASSERTION) | Yes | General AI video engine; skip. |
| [BrokenSource/DepthFlow](https://github.com/BrokenSource/DepthFlow) | 1,547 | 2026-08-25 | AGPL-3.0 | n/a | Do not embed. |
| [provos/parallax-maker](https://github.com/provos/parallax-maker) | 105 | 2026-09-25 | AGPL-3.0 | n/a | Do not embed. |
| [dungthanhluudhl-ui/vox-style-2-codex](https://github.com/dungthanhluudhl-ui/vox-style-2-codex) | 0 | 2026-08-24 | no file | ? | Only the default Remotion README is visible. |
| [gist: holy-templar "vox-explainer-method"](https://gist.github.com/holy-templar/4d6fada5f6041654a8efbefedf4eb142) | n/a | 2026-08-06 | none stated | No | Paid MaxFusion AI-video method. The gist is written as setup instructions addressed to agents; treated as data, nothing acted on. |

Takeaway: the popular "Vox" skills are AI-video pipelines (image model poster, then image-to-video). Only a few repos do deterministic Remotion collage, and the only MIT ones with reusable React are the faceless-shorts collage kit and the voxstylehub validators. The rest of the look has to be built from Remotion primitives and small libraries, which is feasible.

Our own prior art: `nexa-video-creator/template/src/scenes.tsx` already has a seeded `Scribble` underline (`random()`), a `Paper` dot grid (CSS `radial-gradient`), `Bubbles` and `Chip`; `vox.tsx` is currently a placeholder. `codex-imagegen cutout` removes flat, border-connected backgrounds only, so real photographs still need the Vision tool from section 4.1. The team's own earlier research (`claude-agency-designer-set-by-codex/codex-design/references/research/R6-rendering-tooling.md`) reached the same rembg conclusion: Vision first, `birefnet-general` as fallback.

---

## 3. Techniques

### 3.1 Determinism rules (Remotion renders frames out of order, in parallel tabs)

1. Every visual value is a pure function of `useCurrentFrame()` and props. No state or refs carrying values between frames.
2. Randomness only through `random(seed)` from `remotion`, `@remotion/noise`, roughjs `seed` (its default seed is random, so always pass one), `@remotion/rough-notation` `seed`, and effect `seed` params. Never `Math.random()` or `Date.now()`.
3. No CSS animations or transitions, no `d3-transition`, no R3F `useFrame`, no Lottie autoplay (use `@remotion/lottie`), no GSAP autoplay (use `@remotion/gsap`).
4. Load through Remotion-aware components (`<Img>`, `<CanvasImage>`, `<Video>`, `<AnimatedImage>`, `<Lottie>`) or wrap custom loads in `delayRender()`. Avoid CSS `background-image: url()` and `mask-image: url()`: the renderer does not wait for them.
5. Fonts through `@remotion/google-fonts` or `@remotion/fonts`; measure text only after `waitUntilDone()`.
6. Particles (embers, smoke, confetti): closed-form position from seeded initial values, `p(t) = p0 + v*t + 0.5*g*t^2`; never step a simulation per frame (bake it to JSON offline if needed).
7. Check: render the same frame range (for example `--frames=100-160 --image-format=png`) as an image sequence once at `--concurrency=1` and once at `--concurrency=7`, then diff the PNGs; any difference means hidden state or unseeded randomness.

### 3.2 Locked paper background and grain

- **Paper plate**: render once, reuse forever. Either a CC0 paper scan (ambientCG "Paper001"/"Paper005", Poly Haven) or bake Remotion's own `paper()` at 3840x2160 with `npx remotion still PaperPlate public/fx/paper.jpg --image-format=jpeg --jpeg-quality=92 --gl=angle`, then show it with `<Img>` outside the camera group so it stays locked. Oversize by the largest push-in (for example 1.12x) if the paper takes part in the move. The current `Paper` component's full-frame `radial-gradient` is also a per-frame paint cost; bake it too.
- **Grain**: either `noise()` on one full-frame `<Solid>` (`seed` from the frame, one WebGL canvas) or eight baked mid-grey JPEG grain frames blended with `overlay` (no WebGL at all). Changing grain "on twos" reads as film rather than digital noise.

```python
# make_grain.py: 8 full-HD grain frames, identical on every build
import numpy as np
from PIL import Image
rng = np.random.default_rng(7)
for i in range(8):
    g = rng.normal(128, 20, (1080, 1920)).clip(0, 255).astype(np.uint8)
    Image.fromarray(g).save(f"public/fx/grain-{i}.jpg", quality=90)  # mid grey is neutral under overlay
```

```tsx
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.16}) => {
  const k = Math.floor(useCurrentFrame() / 2) % 8; // new grain every second frame
  return (
    <AbsoluteFill style={{mixBlendMode: 'overlay', opacity, pointerEvents: 'none'}}>
      {Array.from({length: 8}, (_, i) => (
        <Img key={i} src={staticFile(`fx/grain-${i}.jpg`)}
          style={{position: 'absolute', inset: 0, width: '100%', height: '100%', display: i === k ? 'block' : 'none'}} />
      ))}
    </AbsoluteFill>
  );
};
```

All eight images stay mounted (and loaded) and only `display` toggles, so no frame waits on a fetch.

### 3.3 Black-and-white halftone people with an offset red marker stroke

Three routes, in order of preference for production:

1. **Bake offline (default)**: Vision cutout, then a baker writes `person.halftone.png` (dots only, alpha kept) and `person.backing.png` (ragged red blob, offset). At render time they are two `<Img>` layers: backing draws on first (clip-path wipe along the stroke direction), then the person pops in. Zero WebGL, trivially cached, looks identical everywhere.
2. **Runtime effects (hero shots, previews)**: two `<CanvasImage>` layers with `@remotion/effects`, sketched below. Costs one to two WebGL chains per person.
3. **Pure CSS/SVG halftone** (radial-gradient dot pattern + `mix-blend-mode: multiply` + a high `contrast()` filter, see Frontend Masters and CSS IRL articles): works for flat graphics, but the contrast filter and blend on every layer is exactly what Remotion lists as slow. Not recommended for many layers.

Halftone baker (Pillow; `python-halftone` has no licence, so we write our own):

```python
import math
from PIL import Image, ImageChops, ImageDraw, ImageOps
def halftone(src: str, dst: str, cell: int = 9, angle: float = 45, ink=(22, 22, 22)) -> None:
    im = Image.open(src).convert("RGBA"); w, h = im.size
    flat = Image.alpha_composite(Image.new("RGBA", (w, h), "white"), im).convert("L")
    tone = ImageOps.autocontrast(flat, cutoff=1).rotate(angle, expand=True, fillcolor=255)
    cells = tone.resize((tone.width // cell, tone.height // cell), Image.Resampling.BOX)  # mean tone per cell
    dots = Image.new("L", tone.size, 0)
    draw = ImageDraw.Draw(dots)
    for y in range(cells.height):
        for x in range(cells.width):
            r = cell * 0.71 * math.sqrt(1 - cells.getpixel((x, y)) / 255)  # dot area follows darkness
            cx, cy = (x + 0.5) * cell, (y + 0.5) * cell
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    dots = dots.rotate(-angle, expand=True)
    l, t = (dots.width - w) // 2, (dots.height - h) // 2
    alpha = ImageChops.multiply(dots.crop((l, t, l + w, t + h)), im.getchannel("A"))
    Image.merge("RGBA", (*(Image.new("L", (w, h), c) for c in ink), alpha)).save(dst)
```

Red marker backing baker (dilate, roughen only the edge, offset):

```python
import numpy as np
from PIL import Image, ImageFilter, ImageOps
def marker_backing(src: str, dst: str, grow=24, offset=(16, 12), rgb=(214, 43, 36), seed=7) -> None:
    im = Image.open(src).convert("RGBA")
    pad = grow + max(offset) + 12
    a = ImageOps.expand(im.getchannel("A"), pad, fill=0)
    blob = a.filter(ImageFilter.GaussianBlur(grow)).point(lambda v: 255 if v > 12 else 0)  # grow silhouette
    soft = blob.filter(ImageFilter.GaussianBlur(5))
    grain = Image.fromarray(np.random.default_rng(seed).integers(0, 256, soft.size[::-1], dtype=np.uint8))
    mask = Image.blend(soft, grain.filter(ImageFilter.GaussianBlur(1.5)), 0.35).point(lambda v: 255 if v > 110 else 0)
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", a.size, (*rgb, 255)), offset, mask)  # save here to animate the backing alone
    out.alpha_composite(ImageOps.expand(im, pad, fill=(0, 0, 0, 0)))
    out.save(dst)
```

Runtime alternative (verify visually; `outlineOnly` returns a filled, grown silhouette in the outline colour):

```tsx
import {CanvasImage, staticFile} from 'remotion';
import {outline} from '@remotion/effects/outline';
import {roughenEdges} from '@remotion/effects/roughen-edges';
import {grayscale} from '@remotion/effects/grayscale';
import {levels} from '@remotion/effects/levels';
import {halftone} from '@remotion/effects/halftone';
const src = staticFile('cut/minister.png');
export const HalftonePerson: React.FC = () => (<>
  <CanvasImage src={src} width={900} height={1100} fit="contain" style={{position: 'absolute', left: 520, top: 40, translate: '18px 14px'}}
    effects={[outline({width: 28, color: '#d62b24', outlineOnly: true}), roughenEdges({border: 18, scale: 0.08, seed: 4})]} />
  <CanvasImage src={src} width={900} height={1100} fit="contain" style={{position: 'absolute', left: 520, top: 40}}
    effects={[grayscale(), levels({blackPoint: 0.08, whitePoint: 0.9}), halftone({dotSize: 9, dotSpacing: 9, rotation: 45, dotColor: '#161616'})]} />
</>);
```

Marker strokes and highlighters elsewhere (underlines, circles around words, arrows): `@remotion/rough-notation` for text, `perfect-freehand` for free strokes. `perfect-freehand` is deterministic for identical points, so jitter the centre line once with `random(seed)` and reveal by slicing points:

```tsx
import {getStroke} from 'perfect-freehand';
import {interpolate, random, useCurrentFrame} from 'remotion';
const toD = (p: number[][]) => (p.length ? `M${p.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join('L')}Z` : '');
export const MarkerSwipe: React.FC<{w: number; seed: string; from: number; to: number}> = ({w, seed, from, to}) => {
  const line = Array.from({length: 40}, (_, i) => [(i / 39) * w, 30 + (random(`${seed}-${i}`) - 0.5) * 6, 0.6]);
  const n = Math.round(interpolate(useCurrentFrame(), [from, to], [2, line.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const outline = getStroke(line.slice(0, n), {size: 44, thinning: 0.2, smoothing: 0.6, streamline: 0.3, simulatePressure: false, end: {taper: 18}});
  return <svg width={w} height={60} style={{mixBlendMode: 'multiply'}}><path d={toD(outline)} fill="#f2d33b" /></svg>;
};
```

### 3.4 Colour cutouts of buildings and objects

- Vision cutout, crop to the alpha bounding box, cap the long side at the largest on-screen size times the largest push-in (for example 1.3x).
- White sticker edge: bake (same dilation as the marker backing, filled white) or `outline({width: 10, color: '#fffaf0'})` at runtime.
- Shadow: bake a separate `*.shadow.png` (alpha blurred 12 to 20 px, 20 to 30 percent black, offset down-right) and animate it with the object, so lifts and drops can change offset and opacity without any CSS filter. Use one GPU `dropShadow()` only when the shadow must change shape.
- Parallax: give each object a `depth` (section 3.12).

### 3.5 Newspaper and document mock-ups with highlighted lines

- Build documents in HTML/CSS with real, editable text: `columnCount`, `columnRule`, justified serif (Old Standard TT, Libre Caslon Text, Source Serif 4), a masthead face, datelines in small caps, a slight `rotate`, a baked shadow plate underneath, and a paper texture on top with `mix-blend-mode: multiply` (one full-frame blend layer is fine).
- Highlights: `<Highlight progress={...} seed={n}>` from `@remotion/rough-notation` for marker look; or a plain yellow bar per line with `mix-blend-mode: multiply` and `scale` along x from 0 to 1 (`transformOrigin: 'left'`), staggered 4 to 6 frames per line. The official News Article Highlight element uses `<Highlight>` with `Easing.spring` progress.
- Real scans or screenshots: get line boxes with Apple Vision `VNRecognizeTextRequest` (local, free) instead of Tesseract, then position highlight bars from the returned bounding boxes.
- Push in on the highlighted line with the camera (section 3.12).

### 3.6 Animated maps

**Data and licences**

| Data or library | Licence | Notes |
|---|---|---|
| Natural Earth 5.1.2 (vector, 1:10m/50m/110m) | Public domain | Default boundaries are de facto; point-of-view variants for 31 countries including Bangladesh, India, Pakistan, China, Nepal. Pick the POV that matches the audience and record it in the production notes. |
| `world-atlas` 2.0.2 | ISC (data: Natural Earth 4.1.0) | Ready TopoJSON (`countries-50m.json`, `land-110m.json`); repo archived since 2021, data older than NE 5.1. |
| `us-atlas` 3.0.1 | ISC (data: US Census 2017 cartographic boundaries) | States and counties, optional Albers-projected variants. |
| `d3-geo` 3.1.1, `d3-geo-projection` 4.0.0 | ISC | Projections, `geoPath`, `geoInterpolate`, `geoGraticule10`. |
| `topojson-client` 3.1.0, `topojson-server` 3.0.1 | ISC | TopoJSON to GeoJSON and back. |
| `mapshaper` 0.7.67 | MPL-2.0 (CLI) | Convert NE shapefiles, filter countries, simplify, write TopoJSON at build time. |
| `@turf/turf` 7.4.0 | MIT | Distances, slicing lines along a route. |
| `polylabel` 2.1.0 | ISC | Label anchor at the pole of inaccessibility (centroids drift to edges). |
| `maplibre-gl` 6.11.2 | BSD-3-Clause | Only for real basemaps; tile and style providers have their own terms and attribution. |

**Recommended approach for the paper map look**: SVG.

1. Build step: `mapshaper` filters and simplifies Natural Earth (POV as needed), then a Node script projects once with d3-geo and writes `map.json` with SVG path strings, label anchors (polylabel) and per-country metadata. Each render tab then loads a small JSON instead of re-projecting 10m geometry.
2. Render: `<path d>` per country with paper fills; borders draw with `evolvePath`; routes use `geoInterpolate` (great circle) sampled to 64 points; a marker follows `getPointAtLength` and rotates with `getTangentAtLength`; label chips pop in with a spring at their anchors.
3. Camera: zoom and pan a `<g transform>` inside the SVG (vectors re-rasterize crisply, unlike the MapLibre shimmer case) and use `vectorEffect="non-scaling-stroke"` so borders keep their width while zooming.
4. Fills: country reveals by clip-path (circle radius or rising "liquid fill" rect clipped to the country path); oceans with `waves()`/`lines()` patterns or a slow hatch drift.
5. Faux 3D: stack 10 to 14 copies of a highlighted country path offset in y in a darker shade under the top face, optionally tilt the whole SVG plane with `perspective(1800px) rotateX(38deg)`. For real lighting use `@remotion/three`: d3 path to `SVGLoader.createShapes()` to `ExtrudeGeometry`, driven by the frame (needs `--gl=angle`).

```tsx
import {geoInterpolate, geoNaturalEarth1, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import world from 'world-atlas/countries-50m.json';
import {evolvePath, getLength, getPointAtLength} from '@remotion/paths';
import {interpolate, useCurrentFrame} from 'remotion';
const land = feature(world as any, (world as any).objects.countries) as any;
const proj = geoNaturalEarth1().fitExtent([[40, 40], [1880, 1040]], land);
const shapes: string[] = land.features.map((f: any) => geoPath(proj)(f) ?? ''); // once per tab, not per frame
const arc = geoInterpolate([90.41, 23.81], [-0.13, 51.51]); // Dhaka to London, great circle
const route = 'M' + Array.from({length: 65}, (_, i) => proj(arc(i / 64))!.join(',')).join('L');
export const RouteMap: React.FC = () => {
  const p = interpolate(useCurrentFrame(), [15, 75], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const head = getPointAtLength(route, getLength(route) * p);
  return (<svg viewBox="0 0 1920 1080">
    {shapes.map((d, i) => <path key={i} d={d} fill="#e8dcc2" stroke="#7d705a" strokeWidth={0.8} />)}
    <path d={route} fill="none" stroke="#d62d20" strokeWidth={7} strokeLinecap="round" {...evolvePath(p, route)} />
    <circle cx={head.x} cy={head.y} r={11} fill="#d62d20" />
  </svg>);
};
```

Border draw for multi-part countries (islands, exclaves): split into subpaths and spend one progress value across their cumulative length, which is also how the official MapTiler technique treats MultiLineStrings.

```tsx
import {evolvePath, getLength, getSubpaths} from '@remotion/paths';
export const BorderDraw: React.FC<{d: string; progress: number}> = ({d, progress}) => {
  const parts = getSubpaths(d).map((sub) => ({sub, len: getLength(sub)})); // memoise per shape in real code
  const total = parts.reduce((s, p) => s + p.len, 0);
  let before = 0;
  return (<g fill="none" stroke="#1d1d1b" strokeWidth={3} strokeLinejoin="round">
    {parts.map(({sub, len}, i) => {
      const local = Math.min(1, Math.max(0, (progress * total - before) / len));
      before += len;
      return <path key={i} d={sub} {...evolvePath(local, sub)} />;
    })}
  </g>);
};
```

Timing idea from the official map explainer rule: drive border draws by "seconds since this country's trigger" with a constant duration, not by a slice of a global progress, otherwise long borders flash by.

### 3.7 Line and bar charts, price tags with counters

- `d3-scale` for domains and ticks, `d3-shape` for `line`, `area`, `curveMonotoneX`; render JSX; animate the line with `evolvePath`, bars with a staggered `scale` along y (3 to 5 frames apart, per the template rules), and fade value labels in after each bar lands.
- Counters: `Math.round(interpolate(...))` formatted with `Intl.NumberFormat` (currency, compact), `fontVariantNumeric: 'tabular-nums'` so digits do not jitter, `Easing.out(Easing.exp)` or `Easing.out(Easing.cubic)`. The price tag itself is an SVG tag shape (rounded rect plus eyelet hole and string) rotated a few degrees, popping in with `spring()`; a red slash through an old price uses `<StrikeThrough>` or `<CrossedOff>`.

```tsx
import {scaleLinear} from 'd3-scale';
import {curveMonotoneX, line} from 'd3-shape';
import {evolvePath} from '@remotion/paths';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
const data = [[2019, 12], [2020, 9], [2021, 15], [2022, 22], [2023, 31]] as const;
const x = scaleLinear().domain([2019, 2023]).range([180, 1740]);
const y = scaleLinear().domain([0, 35]).nice().range([900, 180]);
const d = line<readonly [number, number]>().x((p) => x(p[0])).y((p) => y(p[1])).curve(curveMonotoneX)(data)!;
export const PriceLine: React.FC = () => {
  const p = interpolate(useCurrentFrame(), [10, 70], [0, 1], {easing: Easing.bezier(0.33, 0, 0.2, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<svg viewBox="0 0 1920 1080">
    {y.ticks(5).map((t) => (<g key={t}><line x1={180} x2={1740} y1={y(t)} y2={y(t)} stroke="#0002" />
      <text x={150} y={y(t) + 10} textAnchor="end" fontSize={30}>{t}</text></g>))}
    <path d={d} fill="none" stroke="#111" strokeWidth={8} strokeLinecap="round" {...evolvePath(p, d)} />
  </svg>);
};
```

### 3.8 Speech bubbles

`<Callout>` from `@remotion/shapes` gives the bubble with a pointer in any direction; for a hand-drawn edge, pass `makeCallout(...).path` to `rough.generator().path(d, {seed, roughness: 1.2})` and render `toPaths()` output (roughjs is MIT and already a dependency of rough-notation).

```tsx
import {Callout} from '@remotion/shapes';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
export const Bubble: React.FC<{text: string; at: number}> = ({text, at}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - at, fps, config: {damping: 12, stiffness: 180}});
  return (<div style={{position: 'absolute', left: 1180, top: 140, scale: String(pop), transformOrigin: '20% 100%'}}>
    <Callout width={560} height={220} cornerRadius={36} pointerDirection="down" pointerPosition={0.2} pointerLength={70} fill="#fffdf6" stroke="#161616" strokeWidth={6} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 560, height: 220, display: 'grid', placeItems: 'center', font: '700 54px "Source Serif 4"'}}>{text}</div>
  </div>);
};
```

### 3.9 Typewriter quote

Slice the string by frame (template rule: never per-character opacity), keep the caret solid while typing and blink it smoothly after. For Bangla, slice by grapheme clusters with `Intl.Segmenter`, otherwise vowel signs and hasanta sequences break mid-cluster (current ICU applies the Unicode 15.1 Indic conjunct rules to Bengali).

```tsx
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
const seg = new Intl.Segmenter(undefined, {granularity: 'grapheme'});
export const Typewriter: React.FC<{text: string; cps?: number}> = ({text, cps = 14}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const g = [...seg.segment(text)].map((s) => s.segment);
  const n = Math.min(g.length, Math.floor((frame / fps) * cps));
  const caret = n < g.length ? 1 : interpolate(frame % 16, [0, 8, 16], [1, 0, 1]);
  return (<p style={{fontFamily: 'Special Elite', fontSize: 64, whiteSpace: 'pre-wrap'}}>
    {g.slice(0, n).join('')}<span style={{opacity: caret}}>|</span></p>);
};
```

Place the quote on a paper card, add quote marks as separate large glyphs, and highlight the key phrase after typing ends.

### 3.10 Burning banknote

Options, best first:

1. **Custom WebGL2 effect** via `createEffect()` on `<CanvasImage src="note.png">`: a noise field plus a directional gradient compared against `progress` gives the burn front; a thin orange rim is the ember line, a wider brown band ahead of it is the char. Deterministic by `progress` and `seed`. Add seeded ember sprites (closed-form arcs), a little `noiseDisplacement()` above the front for heat haze, and a stylised Lottie flame (Lottie Simple License) riding the front if the scene needs visible flames. Technique references: Kyle Halladay's burning-paper dissolve and the gameidea edge-burn shader (concepts only; write our own code).
2. **Pre-rendered alpha loop**: render our own burn once from Remotion as VP9 alpha WebM (`--codec=vp9 --pixel-format=yuva420p --image-format=png`) and place it with `<Video>`; good when many notes burn.
3. **Stock fire with alpha**: only with a licence that allows automated pipelines (ProductionCrate forbids it; Envato Elements is a subscription with per-project licence registration and Pond5 sells per clip, so check both for automated use). Fire on black can be composited with `mixBlendMode: 'screen'` (Remotion docs) but still needs a clean licence.
4. **SVG `feTurbulence` + `feComponentTransfer` threshold mask**: deterministic (fixed `seed` attribute) but CPU-rasterized every frame; acceptable for a small element only.

Fragment core for option 1 (drop into the WebGL2 boilerplate from `remotion-markup/effects.md`; `calculateKey` must include `progress` and `seed`):

```glsl
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + uSeed * 17.0) * 43758.5453); }
float vnoise(vec2 p) {
  vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}
void main() {
  vec4 src = texture(uSource, vUv);                                      // premultiplied alpha
  float n = 0.55 * vnoise(vUv * 5.0) + 0.3 * vnoise(vUv * 13.0) + 0.15 * vnoise(vUv * 37.0);
  float d = (0.6 * n + 0.4 * (1.0 - vUv.y)) - (uProgress * 1.25 - 0.15);  // distance ahead of the burn front
  float alive = step(0.0, d);
  float ember = alive * (1.0 - smoothstep(0.0, 0.035, d));               // thin glowing rim
  float scorch = alive * (1.0 - smoothstep(0.0, 0.16, d));               // brown char band ahead of it
  vec3 rgb = mix(src.rgb, vec3(0.10, 0.06, 0.03) * src.a, scorch * 0.85);
  rgb += vec3(1.0, 0.42, 0.06) * ember * 1.8 * src.a;
  fragColor = vec4(rgb, src.a) * alive;
}
```

Currency note: US law (18 U.S.C. 504) allows depictions of currency in motion pictures and television; other countries have their own rules, so a stylised or clearly fictional note is the safe default for generic stories.

### 3.11 Paper wipes and tears

- **Paper-sheet overlay wipe (default)**: a baked sheet PNG with a torn leading edge and baked shadow slides across and off inside a `TransitionSeries.Overlay`; the cut happens underneath. One `<Img>`, transforms only, timeline not shortened.
- **Torn-edge slide-over presentation**: the entering scene slides in on top with a seeded jagged left edge and a shadow (the entering scene renders above the exiting one in `TransitionSeries`).
- **`tear()` inside `<HtmlInCanvas>`** (official Tear element pattern) for a real rip of the outgoing frame: WebGL, unstable Chrome API, no nesting, so spike first.
- **gl-transitions** (MIT) through `makeHtmlInCanvasPresentation` for anything else shader-based.

```tsx
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';
import {AbsoluteFill, interpolate, random} from 'remotion';
type P = {seed: string};
const torn = (seed: string, x: number) =>
  Array.from({length: 41}, (_, i) => `${x + random(`${seed}-${i}`) * 1.6}% ${(i / 40) * 100}%`).join(', ');
const PaperSlide: React.FC<TransitionPresentationComponentProps<P>> = ({children, presentationDirection, presentationProgress: p, passedProps}) => {
  if (presentationDirection === 'exiting') return <AbsoluteFill>{children}</AbsoluteFill>;
  const edge = interpolate(p, [0, 0.85, 1], [0, 0, -3]); // push the ragged margin off-screen at the end
  return (
    <AbsoluteFill style={{translate: `${(1 - p) * 100}% 0`, filter: 'drop-shadow(-14px 0 16px rgba(40,28,12,.35))'}}>
      <AbsoluteFill style={{clipPath: `polygon(${torn(passedProps.seed, edge)}, 100% 100%, 100% 0%)`}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
export const paperSlide = (props: P): TransitionPresentation<P> => ({component: PaperSlide, props});
```

The outer wrapper carries the shadow because CSS applies `filter` before `clip-path` on the same element; the `drop-shadow` only runs for the transition's frames.

### 3.12 2.5D parallax and push-ins

- **Collage layers**: every layer has a `depth` (0 = paper, 1 = nearest). The camera zooms about the frame centre; nearer layers scale and pan faster. Keep the paper plate outside the camera for the locked look. Use `Easing.bezier(0.33, 0, 0.2, 1)` or `Easing.spring({damping: 200})`, and `output: 'perceptual-scale'` (4.0.490+) when interpolating scale. Size bitmaps so the largest push never upscales them. For a stop-motion feel, `posterize: 2` in `interpolate()`.
- **Photos**: depth map from Depth Anything V2 Small (Apache-2.0, Core ML build for Apple silicon), then either split into 3 or 4 depth slices with inpainted gaps (LaMa, Apache-2.0) and animate them as collage layers, or displace a subdivided plane in `@remotion/three` with the depth map (frame-driven camera, `--gl=angle`).

```tsx
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
type Layer = {src: string; x: number; y: number; w: number; depth: number}; // depth 0 = paper, 1 = nearest
export const CollageCamera: React.FC<{layers: Layer[]; push?: number; pan?: number}> = ({layers, push = 0.1, pan = -50}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, width, height} = useVideoConfig();
  const t = interpolate(frame, [0, durationInFrames - 1], [0, 1], {easing: Easing.bezier(0.33, 0, 0.2, 1)});
  return (<AbsoluteFill>
    {layers.map((l, i) => (
      <Img key={i} src={staticFile(l.src)} style={{
        position: 'absolute', left: l.x, top: l.y, width: l.w,
        transformOrigin: `${width / 2 - l.x}px ${height / 2 - l.y}px`, // zoom about the frame centre
        scale: String(1 + push * t * (0.6 + 0.8 * l.depth)),          // nearer layers grow faster
        translate: `${pan * t * (0.3 + l.depth)}px 0px`,
      }} />
    ))}
  </AbsoluteFill>);
};
```

Add idle "breathing" on each layer with `noise2D(seed, frame / 90, 0)` (a few pixels and a fraction of a degree) so nothing sits dead still, as the faceless-shorts design note recommends.

---

## 4. Asset pipeline

### 4.1 Background removal on macOS without paid APIs

**Apple Vision (first choice)**. `VNGenerateForegroundInstanceMaskRequest` (macOS 14+, iOS 17+) finds salient foreground instances; `VNInstanceMaskObservation.generateMaskedImage(ofInstances:from:croppedToInstancesExtent:)` returns a high-resolution image where everything except the chosen instances is transparent black. `generateScaledMaskForImage(forInstances:from:)` returns the soft mask if we want our own matting. `VNGeneratePersonInstanceMaskRequest` (macOS 14+) separates individual people. The Swift-only API `GenerateForegroundInstanceMaskRequest` needs macOS 15+. It is the model behind Finder and Preview's Remove Background, so there is no model licence to track. Normalise EXIF orientation before calling it (for example `ImageOps.exif_transpose`).

```swift
// vision-cutout.swift (macOS 14+). Build: swiftc -O vision-cutout.swift -o vision-cutout
import Vision
import CoreImage
import Foundation
let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1]), output = URL(fileURLWithPath: args[2])
let handler = VNImageRequestHandler(url: input)
let request = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([request])
guard let obs = request.results?.first else { FileHandle.standardError.write("no subject\n".data(using: .utf8)!); exit(2) }
let buffer = try obs.generateMaskedImage(ofInstances: obs.allInstances, from: handler, croppedToInstancesExtent: true)
try CIContext().writePNGRepresentation(of: CIImage(cvPixelBuffer: buffer), to: output, format: .RGBA8,
                                       colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!, options: [:])
```

`stroniarz/remove-bg` (MIT) is a complete 70-line version with a Claude Code SKILL.md, useful as a reference. The same Swift binary can grow a `--ocr` mode with `VNRecognizeTextRequest` for document highlights (section 3.5).

**rembg (fallback, local)**. rembg 2.0.85 (code MIT) needs Python 3.11+ (run it in a `uv` venv) and onnxruntime. Since 2.0.80 its default model is `bria-rmbg` (RMBG-2.0, "requires a paid agreement for commercial use"), so always pass `-m`: `birefnet-general` or `birefnet-portrait` (BiRefNet, MIT), `isnet-general-use` (DIS, Apache-2.0), `u2net` / `u2net_human_seg` (U-2-Net, Apache-2.0), `sam` (Apache-2.0). Never use the `withoutbg` backend (it uploads images to a third-party API). Alpha matting (`-a`) helps hair; the README suggests color decontamination (`-dc`) first for the newer models.

### 4.2 Where cutouts come from

| Source | Licence | Use it for | Watch out for |
|---|---|---|---|
| Smithsonian Open Access, The Met Open Access | CC0 | Archival objects, art, historical photos | Only items marked CC0. |
| US federal government works (official portraits, NASA, agencies) | Public domain in the US | Politicians and officials in US stories | Trademarks and insignia; public domain elsewhere varies. |
| Wikimedia Commons | Varies per file (PD, CC0, CC BY, CC BY-SA) | Public figures, buildings | Record the licence and author per file; CC BY and BY-SA need on-screen or description credit. |
| Unsplash, Pexels | Free licences, commercial use allowed | Generic people, buildings, objects | No standalone resale or competing service; identifiable people must not be shown in a bad light (Pexels); trademarks. |
| Pixabay | Content License | Same | No standalone redistribution; trademarks; no offensive use of identifiable people. |
| ambientCG, Poly Haven | CC0 | Paper, cardboard, fabric textures | None; safe to commit to the public repo. |
| Texturelabs | Free for commercial video, no redistribution | Paper, tape, grunge | Never commit to the public repo or ship in templates. |
| AI generation (`codex-imagegen`) | OpenAI's terms assign output rights to the user, who carries infringement risk | Generic people, props, buildings, textures | No real, identifiable people generated from scratch; keep real people to licensed photos. |

For every asset, write a manifest line (source URL, licence, author, date retrieved, whether it shows a real person, and the Natural Earth POV used for maps). `niovideoshelp-jpg/documentary-remotion`'s `ASSETS.md` is a good pattern.

### 4.3 Transparent ocean or water loops

Free water loops with a real alpha channel are rare; Vecteezy and Videezy "free" clips usually carry attribution requirements (check each clip), and alpha-channel water on Envato Elements (subscription) and Pond5 (per clip) is paid. For a paper map, generate water ourselves: slow hatch lines or `waves()` stripes masked to the ocean shape, or animated SVG sine paths with `@remotion/noise` offsets. If many scenes need the same loop, render it once from Remotion as VP9 alpha WebM or ProRes 4444 and place it with `<Video>` from `@remotion/media`. VP9 alpha needs `-auto-alt-ref 0` when encoded outside Remotion; Safari cannot play VP9 alpha, which does not matter for rendering.

### 4.4 Asset contract

- Crop every cutout to its alpha bounding box; cap the long side at (max on-screen size x max zoom), typically 1,600 to 2,400 px for people at 1080p.
- Formats: PNG (or lossless WebP) for anything with alpha, JPEG for full-frame opaque plates (paper, grain), JSON for map geometry. Benchmark before switching to AVIF, which is generally slower to decode.
- Naming: `cut/<slug>.png`, `cut/<slug>.halftone.png`, `cut/<slug>.backing.png`, `cut/<slug>.shadow.png`, `fx/paper.jpg`, `fx/grain-0..7.jpg`, `geo/<map>.json`.
- The Python bakers need Pillow and numpy in a `uv` venv (system Python 3.9.6 is too old); `codex-imagegen doctor --setup` already manages Pillow for its own tools. A Node alternative is `sharp` 0.35.4 (Apache-2.0).

---

## 5. Performance

### 5.1 How the renderer spends time

- Local rendering opens `concurrency` browser tabs (default: half the CPU threads, so 7 on this M4 Max), each renders a frame and takes a screenshot; frames are not rendered in order. Each tab has its own JS heap and its own decoded images, so memory and one-off precompute multiply by concurrency.
- Default frame format is JPEG, the fastest; PNG frames are only needed for transparent output.
- `npx remotion benchmark` finds the best concurrency; `--log=verbose` lists the slowest frames.

### 5.2 What is slow

- Remotion's own list: `box-shadow`, `text-shadow`, `background-image: linear-gradient()`, `filter: blur()`, `filter: drop-shadow()`, WebGL (Three.js, Mapbox, Skia), 2D canvas, PNG frames, VP8/VP9 encoding, high resolutions, and the legacy `<Html5Video>`/`<OffthreadVideo>` tags.
- SVG filters: Chrome's design notes say "SVG-on-SVG filters are only rendered using a CPU path"; GPU filtering applies only to already composited sources (canvas, WebGL, video, 3D CSS). `feTurbulence` gets slower with `numOctaves` and filter area. A full-frame turbulence filter re-rasterized every frame is one of the most expensive things we could do; bake textures instead.
- CSS filter chains on many cutouts (the faceless-shorts `Cutout` uses four `drop-shadow()`s for the sticker edge plus one soft shadow per layer) scale badly; bake edges and shadows into PNGs.
- `@remotion/motion-blur` renders N copies of the layer.

### 5.3 Many layered PNGs

- Decoded size is width x height x 4 bytes: a 2,400 x 3,000 cutout is about 29 MB decoded, per tab. Twenty such layers at concurrency 7 is about 4 GB. Pre-size and crop (section 4.4).
- Prefer `<Img>` (native image, cheap composited transforms) over `<CanvasImage>`; use `<CanvasImage>`/`<Img effects>` only when an effect is needed, because it adds a canvas backing store and an effect chain.
- `premountFor` (directly on `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Gif>` since 4.0.497, on `<Video>`/`<Audio>` since 4.0.495, on many more components in 4.0.528) mounts layers early so decoding happens before the first visible frame.
- Keep assets local in `public/` and reference them with `staticFile()`: no network in the render loop, no CORS issues for canvas-based components.
- There is no "offthread image" component: images always decode in the page. The offthread concept only exists for video, and `<OffthreadVideo>` is now the legacy path; `<Video>` from `@remotion/media` is the recommended, faster one.
- Keep blend modes to one or two full-frame layers (grain, paper multiply); do not put `mix-blend-mode` on each cutout.

### 5.4 WebGL effects budget

- WebGL2 effects need `Config.setChromiumOpenGlRenderer('angle')` in `remotion.config.ts` (or `--gl=angle`); on a Mac desktop, `angle` is the recommended backend.
- Remotion's docs warn that "memory leaks are a known problem with `angle`" and recommend splitting long renders. Render per scene (or per `--frames` range) and concatenate with ffmpeg.
- Chrome allows about 16 active WebGL contexts per page and then drops the oldest one, with only a console warning. Every effected component owns its own canvases (a per-component canvas pool in `remotion`'s effect chain), and premounted scenes are mounted too. Budget WebGL-effected layers per scene well below 16, bake the rest, and spike this with our heaviest scene.
- Start WebGL-heavy scenes at concurrency 2 to 4 and benchmark; the official maps guidance uses 1 for live MapLibre.
- Custom canvases need `preserveDrawingBuffer: true` so the screenshot captures them.

### 5.5 Caching and precompute

- Precompute at build time: map projection to SVG path JSON, label anchors, per-country trigger times, chart paths if data is static. Load JSON via import or `calculateMetadata()`.
- At module scope (once per tab): d3 scales, `geoPath` output, `getSubpaths`/`getLength` of large paths, rough.js drawables, perfect-freehand outlines that do not animate.
- Bake expensive procedural visuals once: paper plate, grain frames, halftone and backing PNGs, repeated burn or water loops as alpha video.
- `measureText()` results are cached by `@remotion/layout-utils`.

### 5.6 Suggested render settings on this Mac

- `remotion.config.ts`: `Config.setChromiumOpenGlRenderer('angle')` only if the project uses WebGL effects; otherwise keep the default renderer.
- Run `npx remotion benchmark` once per template. Reasonable starting points before measuring: 7 (the default on this machine) for DOM/SVG-only scenes, 2 to 4 for WebGL-heavy ones.
- Encode with VideoToolbox: `--hardware-acceleration=if-possible --video-bitrate=12M` (CRF is not supported with hardware encoders; about 8M matches software quality at 1080p per Remotion's docs).
- Spot-check with `npx remotion render <id> out/frames --frames=0,90,180 --image-format=png` before a full render.

---

## 6. Open questions and spikes

1. WebGL context budget: one scene with 12 effected cutouts plus a premounted next scene at concurrency 4; watch for context loss.
2. `tear()` on a whole scene inside `<HtmlInCanvas>`: ms per frame and memory growth across a 3-minute render with `--gl=angle`.
3. Baked vs runtime halftone: same shot both ways, compare look (dot scaling differs) and render time.
4. Natural Earth POV choice per client region (Bangladesh audiences versus global) and who signs off on disputed borders.
5. Remotion licence tier for NexaLance (head count) before the first client render.

---

## 7. Sources (all accessed 2026-09-25)

Remotion skills, docs and packages

- Official skills repo: https://github.com/remotion-dev/skills ; install docs: https://www.remotion.dev/docs/ai/skills ; local copies `~/.claude/skills/remotion-*` (stamped 4.0.528)
- Effects: https://www.remotion.dev/docs/effects ; https://www.remotion.dev/docs/effects/api ; https://www.remotion.dev/docs/effects/halftone ; https://www.remotion.dev/docs/effects/paper ; https://www.remotion.dev/docs/effects/noise ; https://www.remotion.dev/docs/effects/roughen-edges ; https://www.remotion.dev/docs/effects/noise-displacement ; https://www.remotion.dev/docs/effects/grayscale ; https://www.remotion.dev/docs/effects/tear ; https://www.remotion.dev/docs/effects/outline ; https://www.remotion.dev/docs/create-effect ; npm tarball `@remotion/effects@4.0.528` (backends and shader read locally)
- Components: https://www.remotion.dev/docs/canvasimage ; https://www.remotion.dev/docs/img ; https://www.remotion.dev/docs/solid ; https://www.remotion.dev/docs/html-in-canvas
- Transitions: https://www.remotion.dev/docs/transitions/presentations/custom ; https://www.remotion.dev/docs/transitions/presentations/custom-html-in-canvas ; https://www.remotion.dev/docs/transitions/transitionseries
- Paths, shapes, noise, highlights: https://www.remotion.dev/docs/paths ; https://www.remotion.dev/docs/paths/evolve-path ; https://www.remotion.dev/docs/shapes ; https://www.remotion.dev/docs/noise ; https://www.remotion.dev/docs/text-highlights
- Other packages: https://www.remotion.dev/docs/animated-emoji ; https://www.remotion.dev/docs/rive ; https://www.remotion.dev/docs/sfx ; https://www.remotion.dev/docs/motion-blur ; https://www.remotion.dev/docs/third-party
- Media and transparency: https://www.remotion.dev/docs/media/video ; https://www.remotion.dev/docs/media/support ; https://www.remotion.dev/docs/videos/transparency ; https://www.remotion.dev/docs/transparent-videos ; https://github.com/remotion-dev/remotion/issues/10968
- Performance and rendering: https://www.remotion.dev/docs/performance ; https://www.remotion.dev/docs/gl-options ; https://www.remotion.dev/docs/flickering ; https://www.remotion.dev/docs/troubleshooting/webgl2-context ; https://www.remotion.dev/docs/terminology/concurrency ; https://www.remotion.dev/docs/renderer/render-media ; https://www.remotion.dev/docs/cli/render ; https://www.remotion.dev/docs/hardware-acceleration
- Maps: https://www.remotion.dev/docs/maps
- Templates, elements, prompts, showcase: https://www.remotion.dev/templates ; https://www.remotion.dev/elements ; https://www.remotion.dev/elements/maps/watercolor-map ; https://www.remotion.dev/elements/data/line-chart ; https://www.remotion.dev/prompts ; https://www.remotion.dev/prompts/news-article-headline-highlight ; https://www.remotion.dev/showcase ; https://github.com/remotion-dev/remotion/tree/main/packages/docs/elements ; https://github.com/remotion-dev/remotion/blob/main/packages/docs/src/data/showcase-videos.tsx ; https://github.com/remotion-dev/template-prompt-to-motion-graphics-saas
- Releases (feature versions): https://github.com/remotion-dev/remotion/releases
- Licence and pricing: https://github.com/remotion-dev/remotion/blob/main/LICENSE.md ; https://www.remotion.pro/license ; https://www.remotion.pro/store
- npm registry metadata via `npm view` for every package version and licence quoted above

Libraries and data

- https://github.com/steveruizok/perfect-freehand ; https://github.com/rough-stuff/rough/wiki ; https://github.com/rough-stuff/rough-notation
- https://github.com/d3/d3-geo ; https://github.com/d3/d3-scale ; https://github.com/d3/d3-shape ; https://github.com/topojson/topojson-client ; https://github.com/topojson/world-atlas ; https://github.com/topojson/us-atlas ; https://github.com/mbloch/mapshaper ; https://github.com/Turfjs/turf ; https://github.com/mapbox/polylabel (npm licence ISC)
- Natural Earth: https://www.naturalearthdata.com/about/terms-of-use/ ; https://www.naturalearthdata.com/blog/admin-0-countries-point-of-views/ ; https://www.naturalearthdata.com/about/disputed-boundaries-policy/ ; https://github.com/nvkelso/natural-earth-vector/releases
- Three.js extrusion: https://threejs.org/docs/pages/ExtrudeGeometry.html ; https://github.com/ftorghele/worldMap
- Halftone: https://frontendmasters.com/blog/pure-css-halftone-effect-in-3-declarations/ ; https://css-irl.info/css-halftone-patterns/ ; https://github.com/philgyford/python-halftone (no licence)
- SVG filters and Chrome: https://tympanus.net/codrops/2019/02/19/svg-filter-effects-creating-texture-with-feturbulence/ ; https://www.chromium.org/developers/design-documents/image-filters/ ; https://github.com/MelodicBloom/svg-filter-lab/blob/main/docs/how-to-implement-performant-svg-filters-without-killing-your-frame-rate.md
- WebGL context limit: https://issues.chromium.org/issues/40939743 ; https://github.com/openlayers/openlayers/issues/16118
- Burn shaders (concepts): https://kylehalladay.com/blog/tutorial/2015/11/10/Dissolve-Shader-Redux.html ; https://gameidea.org/2024/08/24/2d-dissolve-shader-with-edge-burn-burning-paper-shader/
- Shadertoy licence: https://www.shadertoy.com/terms ; gl-transitions (MIT): https://github.com/gl-transitions/gl-transitions
- Alpha video: https://jakearchibald.com/2024/video-with-transparency/
- Currency depiction: https://uscode.house.gov/view.xhtml?req=granuleid%3AUSC-prelim-title18-section504&num=0&edition=prelim

Asset pipeline and licences

- Apple Vision (docs JSON used for availability): https://developer.apple.com/documentation/vision/vngenerateforegroundinstancemaskrequest ; https://developer.apple.com/documentation/vision/vninstancemaskobservation/generatemaskedimage(ofinstances:from:croppedtoinstancesextent:) ; https://developer.apple.com/documentation/vision/generateforegroundinstancemaskrequest ; https://developer.apple.com/documentation/vision/vngeneratepersoninstancemaskrequest
- https://github.com/stroniarz/remove-bg
- rembg: https://github.com/danielgatis/rembg (README, releases v2.0.80 and v2.0.85) ; https://huggingface.co/briaai/RMBG-2.0 ; https://github.com/ZhengPeng7/BiRefNet ; https://github.com/xuebinqin/U-2-Net ; https://github.com/xuebinqin/DIS
- Depth: https://github.com/DepthAnything/Depth-Anything-V2 ; https://huggingface.co/apple/coreml-depth-anything-v2-small ; https://github.com/advimman/lama ; https://github.com/BrokenSource/DepthFlow ; https://github.com/provos/parallax-maker
- Textures and stock: https://docs.ambientcg.com/license/ ; https://polyhaven.com/license ; https://texturelabs.org/terms/ ; https://www.productioncrate.com/terms.html ; https://pixabay.com/service/terms/ ; https://unsplash.com/license ; https://www.pexels.com/license/ ; https://www.si.edu/openaccess/faq ; https://www.metmuseum.org/hubs/open-access ; https://lottiefiles.com/page/license ; https://www.vecteezy.com/free-videos/seamless-loop-water ; https://elements.envato.com/water-alpha-channel-4k-EJRTNM3 ; OpenAI output terms summary: https://www.lawinsider.com/resources/contract-teardown/openais-terms-of-service

GitHub projects: URLs in the table in section 2 (metadata from the GitHub REST API).

Local files consulted (read only): `~/.claude/skills/remotion-*/`, `nexa-media/remotion-broll/node_modules/@remotion/*` (4.0.528 exports), `claude-agency-designer-set-by-codex/nexa-video-creator/template/{package.json,src/scenes.tsx}`, `claude-agency-designer-set-by-codex/codex-imagegen/references/cli.md`, `claude-agency-designer-set-by-codex/codex-design/references/research/R6-rendering-tooling.md`.
