---
name: nexa-remotion-fx
description: "Pixel effects, looks and scene transitions for Remotion videos: the 74 GPU effects of @remotion/effects as clamped presets (grades and LUTs, film grain, glow, halftone, duotone, chromatic aberration, blurs, pixelate, wave, tear, shine, light leaks), whole looks (film, VHS, CRT, newsprint, noir, dreamy, glitch, stop motion), masks (shapes, text filled with video, gradients, wipes), green-screen keying and screen blends, starburst grounds, and TransitionSeries transitions (CSS, 12 WebGL shaders, zoom-through, whip pan, glitch cut, light-leak cross, mask reveals) with timing checks. Use it for any look, effect or transition request, Banglish included ('film look dao', 'glitch effect koro', 'transition smooth koro', 'green screen remove koro'). Part of the nexa-remotion family."
---

# Effects, looks and transitions for Remotion

What happens to the pixels and between the scenes: grades, textures, looks, masks, keys, light and transitions.
Part of the nexa-remotion family (the director skill is `nexa-remotion`; the kit lives in
`~/.claude/skills/nexa-remotion/kit`, and a project made with `nrk.py new` imports these parts from `./kit/fx`).
Every value is a function of the frame, every effect parameter is clamped, and every choice below was checked on
renders of Remotion 4.0.528.

## Fast path

1. **Name the job.** A grade on footage, a look on a whole scene, an accent on one element (shine, leak, glitch
   hit), a mask reveal, a key, or the cuts between scenes. One look per film; accents only on story beats.
2. **Check the ground rules.** Renders need `--gl=angle` (nrk passes it). At most 8 effect hosts alive at once (each
   `Img`/`Video`/`Solid`/`HtmlInCanvas` with WebGL effects holds 2 of Chrome's 16 contexts per tab). No
   HTML-in-canvas inside HTML-in-canvas, and none inside a scene next to a shader transition.
3. **Footage and photos:** effects on the media element itself: `<Img effects={[fx.grade('cinematic'), fx.vignette(),
   fx.grain({frame, fps})]}>` or `lookEffects('film', {frame, fps})`. Grade first, texture next, lens, vignette,
   grain last.
4. **A whole scene (DOM, type, charts):** wrap it in a look: `<FilmLook>`, `<VhsLook>`, `<CrtLook>`,
   `<NewsprintLook>`, `<NoirLook>`, `<DreamyLook>`, `<GlitchLook>`, `<StopMotionLook>`. Keep captions and small
   type crisp by passing them as `overlay`.
5. **Transitions:** list the scenes and let `<Scenes>` build the TransitionSeries and check it; set the
   composition length from `scenesLength(scenes, fps)`. Default to `tr.slide()`, `tr.wipe()` or `tr.fade()`; use a
   character transition (whip, zoom-through, glitch cut, leak, shader) only where the story turns.
6. **Look at it.** `nrk.py stills PROJECT --every 0.25` around every transition and effect beat; full-size
   `nrk.py still` for grain, halftone and edges; make sure no WebGL frame is blank and nothing is half-visible on
   the last frame.

## Components (from `./kit/fx`)

| Component or helper | Use it for | Key props |
|---|---|---|
| `fx.*` | clamped presets of the effects (grade, exposure, levels, lut, grain, noise, vignette, paper, glow, lightLeak, shine, starburst, chromaticAberration, scanlines, barrel, tvSignalOff, pixelate, wave, jitter, blur, zoomBlur, tiltShift, focus, halftone, duotone, tritone, stencil, posterize, colorKey, outline, dropShadow, tear, evolve, pixelDissolve, slices) | per preset; see the module README |
| `grades` | named colorCorrection sets: natural, cinematic, warmFilm, coolNight, bleach, punchy, mono | `fx.grade(name, amount)` |
| `makeCubeLut`, `useLutFile`, `cleanCube` | LUTs from a function or from `public/` | `fn`, `size` 17; `file` |
| `FilmLook`, `VhsLook`, `CrtLook`, `NewsprintLook`, `NoirLook`, `DreamyLook`, `GlitchLook`, `StopMotionLook`, `Look` | a whole treatment on children | `engine` (auto, canvas, css), `strength`, `overlay`, look props |
| `lookEffects`, `filmEffects`... | a look's effect stack for footage | `{frame, fps, unit, strength}` |
| `glitchAt` | deterministic glitch bursts for your own animation | `bursts` or `every`, `length`, `chance` |
| `Grain`, `VignetteOverlay`, `ScanlineOverlay`, `GrilleOverlay`, `RgbSplit`, `Bloom`, `PosterizeCss`, `DustOverlay`, `SlicesCss` | CSS and SVG layers that work anywhere | see the module README |
| `ShapeMask`, `TextMask`, `GradientMask`, `WipeMask` | reveals through shapes, words, gradients, wipes | `shape`, `size`, `at`, timing (`delay`, `duration`, `exit`, `progress`) |
| `ChromaKey`, `keyEffects`, `Blend`, `BlendVideo` | green screen, and footage shot on black or white | `color`, `similarity`, `smoothness`, `spill`, `matte`, `outline`, `shadow`; `mode`, `crush` |
| `LightLeak`, `Starburst`, `Shine` | light over a cut or a title, ray grounds, a sweep over a logo | `seed`, `hue`, `peak`; `rays`, `speed`; `delay`, `angle` |
| `Scenes`, `tr.*`, `planScenes`, `scenesLength` | transitions between scenes with timing checks | `scenes` [{node, duration, transition}], `enter`, `exit` |
| `posterize`, `sliceShift` | the kit's own effects (createEffect, WebGL2) | levels; amount, bands, density, seed, split |

## Craft rules

- **One look, set once.** A look belongs to the film, not to a scene: same grade and grain from the first frame to
  the last. Strength 1 is the designed default; stay between 0.6 and 1.2.
- **Grain is film, not noise.** Re-seed it about 12 times a second (`fx.grain({frame, fps})`, `<Grain hz={12}>`);
  per-frame grain reads as electronic sizzle and multiplies the file size. Amount 0.04 to 0.08 on the effect, 0.2
  to 0.35 layer opacity for the CSS grain. Grain is the last effect in the chain.
- **Weak vignette.** Corners 15 to 35 percent darker, never a visible ring. Lift blacks a little (no pure black)
  for film; keep them deep for noir and trailers.
- **Banding.** 8-bit effects and H.264 band on wide gradients: finish with 2 to 4 percent noise, use one
  `colorCorrection` instead of chained colour effects, avoid huge soft blurs on flat colour.
- **Order of effects:** replacing generators first (starburst, linearGradient), then key or mask, then grade (or
  LUT), stylise (halftone, duotone), texture (paper, scanlines), lens (barrel, fisheye), vignette, grain.
- **Accents are rationed.** A light leak on one or two cuts per minute, a shine on the hero beat (about three in a
  45 s film), a glitch hit on a beat, not a constant state. A full leak covers the frame at its middle: over a
  title use `peak` 0.5 to 0.7.
- **Transitions carry direction.** Slide and whip in the reading direction or the direction of the story; keep one
  family per film (for example slides plus one signature whip). Lengths at 30 fps: cuts for kinetic type, 8 to 12
  frames for social, 15 to 24 for slide, wipe and fade, 11 for a push cut, 20 to 32 for shaders and zoom-throughs.
- **Hold both sides.** A scene must stay readable outside its transitions: `duration` = reading time + the
  transition in + the transition out. `planScenes` warns when a scene is never on screen alone.
- **Keys look real only with matching light.** Grade the subject toward the plate (temperature, contrast), add a
  soft shadow, and never key black: blend footage shot on black with `screen`.
- **Type survives effects.** Small type (under about 60 px at 1080) goes in `overlay`, above halftone, glitch
  slices, barrel and blur. Big display type can take them.

## Recipes

Film look on a whole scene, captions untouched:

```tsx
<FilmLook grain={0.06} warmth={0.25} overlay={<Captions />}>
  <InterviewScene />
</FilmLook>
```

Graded footage with living grain (no DOM needed):

```tsx
const frame = useCurrentFrame();
const {fps, width, height} = useStage();
<Video src={staticFile('broll.mp4')} objectFit="cover" style={{width, height}}
  effects={[fx.grade('cinematic'), fx.vignette({amount: 0.3}), fx.grain({frame, fps, amount: 0.05})]} />
```

A glitch hit on the beat, clean otherwise (frames of the hits from the cue table):

```tsx
<GlitchLook bursts={[{at: 42, frames: 6}, {at: 66, frames: 4, strength: 0.6}]}>
  <TitleCard />
</GlitchLook>
```

Big word filled with footage (English or Bangla):

```tsx
<TextMask text="ঢাকা" src={staticFile('city.mp4')} fillZoom={0.1} outline={{color: 'rgba(255,255,255,0.4)'}} />
```

Presenter on green over a branded ground:

```tsx
<AbsoluteFill>
  <Starburst rays={24} speed={4} />
  <ChromaKey src={staticFile('presenter.mp4')} color="#1fbf4f" similarity={0.34} spill={0.7} matte={{bottom: 0.1}} shadow />
</AbsoluteFill>
```

Scenes with transitions, a sound on the whip, fades at the ends:

```tsx
const scenes: SceneSpec[] = [
  {node: <Hook />, duration: 75, transition: tr.whipPan({sound: {src: staticFile('whoosh.m4a'), lead: 4}})},
  {node: <Problem />, duration: 120, transition: tr.maskReveal({at: [0.7, 0.4], ring: true})},
  {node: <Product />, duration: 150, transition: tr.lightLeakCross()},
  {node: <EndCard />, duration: 90},
];
export const LENGTH = scenesLength(scenes, 30, {enter: tr.fade(), exit: tr.fade({out: true})});
<Scenes scenes={scenes} enter={tr.fade()} exit={tr.fade({out: true})} />
```

A light leak that hides a hard cut without shortening the edit: `transition: tr.leak({hue: 'coral'})` (an overlay).

## Remotion 4.0.528 facts and traps

- Import every effect from its subpath (`import {noise} from '@remotion/effects/noise'`); the package root exports
  only 11 of the 74. Effect factories validate at call time: an out-of-range value (spring overshoot, unclamped interpolate)
  fails the render. The kit's presets clamp everything.
- Effect hosts: `Solid`, `Img`, `CanvasImage`, `HtmlInCanvas`, `Video` from `@remotion/media` (not OffthreadVideo or
  Html5Video), `@remotion/shapes` shapes, Gif, AnimatedImage, Rive. `Img` with effects needs numeric width and
  height (it becomes a canvas; `style.objectFit` sets the fit).
- GL: WebGL effects, canvas looks and shader transitions need `--gl=angle` (or `swangle`); the bundled Chrome
  Headless Shell 149 renders HTML-in-canvas without flags. Studio preview needs Chrome 148+ with
  `chrome://flags/#canvas-draw-element`.
- Measured context limit: 8 hosts with animated WebGL effects render, 10 fail with "WebGL context was lost". Unmounted
  hosts' contexts are dropped first, so paging through Sequences is safe.
- `<HtmlInCanvas>` inside another throws; inside a scene next to a shader transition it waits for "first paint after
  canvas resize" until the 28 s timeout. The kit's looks switch to css there by themselves.
- Measured bug: a shader transition gets no picture of a scene that entered with a CSS transition (the entering CSS
  presentation never captures it), so it plays as a hard cut. `<Scenes>` splits such scenes; by hand, split the
  scene into two sequences (the second one overlapping the first with `offset={-transitionFrames}`).
- `TransitionSeries.Sequence` in 4.0.528 has no `premountFor` in its types (it passes it through at runtime;
  premounting only acts in preview) and does have `offset`. Children must be `.Sequence`, `.Transition`, `.Overlay`
  directly: a wrapper component around them throws.
- Shader presentation factories (except `blurSlide`) require an options object: `dissolve({})`. `dissolve` colours
  must be 6-digit hex. `dreamyZoom` rotation is degrees, `zoomBlur` rotation radians. `blurSlide` eases itself: use
  linear timing.
- `springTiming` needs `durationRestThreshold: 0.001` or it snaps at the end; its length depends on fps unless
  `durationInFrames` is set.
- `fade()` keeps the outgoing scene opaque: transparent scenes need `shouldFadeOutExitingScene: true`
  (`tr.fade({out: true})`).
- `pushCut` hides the incoming scene until `cutProgress`: delay that scene's content by the hidden frames (Scenes
  does this).
- Raw `zoomBlur()` measures `center` y from the bottom; `fx.zoomBlur` takes top-left UV like the other effects.
- `lightLeak` hue turns toward red first (30 coral, 60 rose, 90 magenta, 180 blue, 270 green); progress 0 to 0.5
  reveals, 0.5 to 1 retracts, full cover at 0.5.
- `duotone()` is a hard threshold; the smooth duotone is `thermalVision({palette: [dark, light]})`. `halftone` and
  `dotGrid` output only dots. `glow` and `lightTrail` are one colour and additive.
- `@remotion/light-leaks` and `@remotion/starburst` components still work on 4.0.528 but are deprecated (gone in
  5.0); use the effects on a `Solid`. `<HtmlInCanvasMotionBlur>` is 4.0.529, not available.

## References

- `references/effects-catalogue.md`: all 74 effects by family with parameters, defaults, ranges, backend, cost and
  output behaviour; custom effects with createEffect.
- `references/looks-and-grading.md`: look recipes, grading footage, LUTs, grain and banding, canvas versus css,
  HTML-in-canvas with custom shaders.
- `references/transitions.md`: TransitionSeries, timings, every presentation, custom and shader presentations,
  overlays, sound, the kit's Scenes and presets, decision tables.
- `references/masks-keying-light.md`: masks, text masks, keying and spill, blend modes, light leaks, starburst,
  shine, tear, motion blur.
- `references/performance-and-errors.md`: GL setup, context limits, cost tiers, determinism, Lambda, every error
  message with its fix, version gates.
