# Looks and grading

A look is the treatment of the whole picture: grade, texture, lens, light. This file covers grading footage, LUTs,
grain and banding, the kit's eight looks (what each does in its two engines), how to build a new look, and
HTML-in-canvas with a custom shader for looks the effects cannot make.

## Where the effect runs: four ways

| Content | Use | Why |
|---|---|---|
| A photo or a clip | `effects` on `Img` or `Video` (`@remotion/media`) | the media element is already a canvas; cheapest, works next to any transition |
| A generated ground (rays, stripes, gradient, paper) | `effects` on a `<Solid width height color?>` | a 1x1 colour stretched to the size; transparent when `color` is left out |
| DOM: type, charts, cards, a whole scene | `<HtmlInCanvas width height effects>` (the kit's canvas engine) | paints the DOM into a canvas and runs the chain on the pixels |
| Anywhere HTML-in-canvas cannot run (inside another, next to a shader transition, a preview without the Chrome flag) | CSS and SVG filters (the kit's css engine) | filters, blend modes, SVG turbulence and colour matrices |

The kit's looks pick canvas or css with `engine` ('auto' by default: canvas when it can run here). Pass the engine
explicitly when the Studio preview must match the render.

## Grading footage

- **One pass.** `colorCorrection` applies exposure, white balance, shadows and highlights, whites and blacks,
  contrast, saturation and vibrance in one shader, so there are no 8-bit round trips between steps. The kit's
  `grades`:

| Grade | Settings | Use |
|---|---|---|
| natural | contrast 1.06, shadows 0.05, highlights -0.08, temperature 0.04, vibrance 0.1 | stock footage clean-up |
| cinematic | contrast 1.12, shadows 0.12, highlights -0.18, blacks -0.05, temperature 0.12, saturation 0.92, vibrance 0.15 | trailers, brand films |
| warmFilm | contrast 0.92, blacks 0.22, highlights -0.1, temperature 0.22, tint 0.04, saturation 0.82 | faded print, nostalgia |
| coolNight | exposure -0.15, contrast 1.08, temperature -0.28, tint -0.03, saturation 0.9, vibrance 0.1 | blue hour, tech |
| bleach | contrast 1.28, highlights -0.12, blacks -0.08, saturation 0.45 | gritty, documentary |
| punchy | exposure 0.08, contrast 1.1, shadows 0.15, saturation 1.12, vibrance 0.3 | social, bright products |
| mono | contrast 1.2, saturation 0, shadows 0.06, highlights -0.1 | black and white with body |

- **Match clips before styling them.** Correct exposure and white balance per clip (`exposure`, `whiteBalance`),
  then put the same look on all of them.
- **Levels** remaps black and white points and midtones (gamma above 1 lifts). It cannot lift the output black:
  use `colorCorrection({blacks: 0.1 to 0.3})` or a LUT for faded blacks.
- **Grade under keys.** A keyed subject over a plate needs the plate's temperature and contrast: grade the subject
  toward the plate, not the other way round.

## LUTs

- `lut({content})` takes the text of a 3D `.cube`. Accepted: `LUT_3D_SIZE` 2 to 256, `TITLE`, `DOMAIN_MIN`,
  `DOMAIN_MAX`, comments and blank lines; the number of rows must equal size cubed. `LUT_1D_SIZE`,
  `LUT_3D_INPUT_RANGE` and other directives throw. The kit's `cleanCube(text)` strips unknown directives (a 1D LUT
  still cannot be used).
- Loading: webpack does not import `.cube` as text, so fetch it. The kit's `useLutFile('grades/x.cube')` fetches from
  `public/` holding the render with `delayRender`, cleans it and returns the text (null until then:
  `effects={cube ? [fx.lut(cube)] : []}`). Or fetch it in `calculateMetadata()` and pass it as a prop.
- Made in code: `makeCubeLut((r, g, b) => [r, g, b], 17)` at module level. 17 points is plenty for a look, 33 for a
  precise grade. Parsed LUTs are cached (4 contents): do not cycle through more than 4 per frame.
- A LUT from a grading app expects the footage's colour space (log footage needs a log-to-Rec.709 LUT first).

## Grain, vignette and banding (the craft numbers)

- **Grain at 12 Hz.** Re-seed about 12 times a second (`seed: Math.floor(frame * 12 / fps)`, the kit's `stepSeed`).
  Every-frame grain reads as electronic sizzle and made one render about 9 times larger. 24 Hz reads as a busy video
  camera; TV static (`whiteNoise`) changes every frame on purpose.
- **Amounts.** `noise` 0.04 to 0.08 with `premultiply: true` (grain follows brightness like film, blacks stay clean);
  CSS grain (SVG turbulence overlay) 0.2 to 0.35 opacity. Grain goes last in the chain.
- **Vignette** weak: corners 15 to 35 percent darker, radius 0.65 to 0.78, feather 0.45 to 0.65. A visible ring or a
  dark oval is a mistake.
- **Blacks** lifted a little for film (no pure #000), deep for noir, trailers and luxury.
- **Banding.** 8-bit between effects plus H.264: add 2 to 4 percent noise over gradients, keep gradients to 2 or more
  stops, avoid huge soft blurs on flat colour, render the master with `--crf=14-18` or PNG frames when gradients
  matter.
- **Specular sweeps** (shine) only on named story beats, about three in 45 seconds.

## The kit's looks

Shared props: `engine`, `strength` (0 off, 1 designed, above 1 heavier), `seed`, `width`, `height`, `overlay`
(untouched layers on top), `style`. For footage without DOM: `lookEffects(name, {frame, fps, unit, strength})`.

| Look | Canvas engine | CSS engine | Pairs with |
|---|---|---|---|
| FilmLook | colorCorrection (lifted warm blacks, soft highlights, slight desaturation, 12 Hz exposure flicker), grain 0.07 at 12 Hz, vignette 0.3; gate weave (noise plus 12 Hz jitter, about 1 px) and dust as DOM | sepia, saturate, contrast, brightness flicker, a screened warm lift, SVG grain, radial vignette | trailer, luxury, editorial, nostalgia |
| VhsLook | lifted blacks, extra saturation, horizontal smear (1-axis blur), wobbling RGB split, thin slice jitter, scanlines, per-frame noise, vignette; tracking band, head-switch noise and VT323 OSD text as DOM | RgbSplit, saturate, blur, a screened purple lift, scanlines, grain | retro, 90s, lo-fi music |
| CrtLook | flicker, glow on highlights, rolling scanlines, small RGB split, barrel curve (corners transparent over a black ground), rounded vignette; aperture grille and glass reflection as DOM | contrast, Bloom, scanlines, rounded inner shadow | terminal, gaming, tech retro |
| NewsprintLook | levels lift, black and white, halftone ink dots over a paper `Solid` with the paper effect | dot pattern times the picture, then contrast (dots grow in the darks), ink and paper via blend modes | editorial, collage, vox |
| NoirLook | black and white, contrast 1.35, deep blacks, grain, heavy vignette; optional venetian-blind shadows | grayscale, contrast, grain, vignette | crime, mystery, drama |
| DreamyLook | lifted pastel grade, warm glow on highlights, focus fall-off at the edges, a light haze vignette | contrast, sepia, Bloom, light vignette | wedding, beauty, memories |
| GlitchLook | bursts only: RGB split flipping each frame, torn slices, jitter, sometimes pixel blocks and static; `idle` split between | RgbSplit plus SlicesCss plus jitter | tech, music, error beats |
| StopMotionLook | poses held on twos or threes with `<Freeze>`, a little boil per pose, posterize when `levels` is set | the same, PosterizeCss | craft, paper cut-out, playful |

Glitch timing: `glitchAt(frame, {bursts})` for hits on beats, or `{every: 54, length: 6, chance: 0.85, seed}` for
irregular automatic bursts. Two hits a few frames apart read better than one long one. The first frame of a burst is
the hardest.

### Building a new look

`LookShell` does the layering: `under` (layers behind), the content (children with `contentStyle`), either the
canvas (effects on `HtmlInCanvas`) or the css version (`cssFilter`, `cssWrap`, `cssOverlays`), then `over` and the
caller's `overlay`. `useLookEngine(engine, '<MyLook>')` resolves auto and refuses canvas where it cannot run.

```tsx
export const DuotoneLook: React.FC<LookBaseProps & {dark?: string; light?: string}> = ({engine, dark = '#14213d', light = '#fca311', children, overlay}) => {
  const e = useLookEngine(engine, '<DuotoneLook>');
  return (
    <LookShell engine={e} label="DuotoneLook" overlay={overlay}
      effects={[fx.duotone({dark, light}), fx.noise({amount: 0.02})]}
      cssFilter="grayscale(1) contrast(1.1)"
      cssOverlays={<><AbsoluteFill style={{background: dark, mixBlendMode: 'lighten'}} /><AbsoluteFill style={{background: light, mixBlendMode: 'multiply'}} /></>}>
      {children}
    </LookShell>
  );
};
```

## Look recipes with raw effects

| Look | Stack (in order) |
|---|---|
| Cinematic grade with living grain | colorCorrection (cinematic), vignette 0.35, noise 0.05 premultiply, seed at 12 Hz |
| Vintage print | colorCorrection (blacks 0.6, contrast 0.9, saturation 0.75, temperature 0.25), noise 0.1, warm vignette (#1a0f05); dust: speckle over a warm off-white layer, `size` changed every few frames |
| VHS / CRT | chromaticAberration (3 plus a flicker), scanlines (offset by frame, premultiply), noise, barrelDistortion 0.12, vignette |
| Glitch hit (frames g to g+8) | chromaticAberration spiking 0 to 30 to 0 with the angle flipping every 2 frames, xyTranslate jitter from noise2D, a short pixelate or whiteNoise |
| Neon title | glow (radius 24, intensity 1.6, threshold 0.2, a cyan) on light text in an HtmlInCanvas at pixelDensity 2 |
| Newspaper | grayscale, halftone (8 px, ink #161616, 45 degrees) over off-white, paper |
| Comic dots in colour | halftone source mode (12 px, 15 degrees) over a cream Solid with paper |
| Risograph two-colour | thermalVision [ink, paper], noise, a tiny chromaticAberration |
| Hard stencil | duotone (dark, light, threshold 0.45) |
| Thermal camera | thermalVision default palette, scanlines, noise |
| Tilt shift | radialProgressiveBlur (a wide flat ellipse, start 0.35, 30 px), saturation 1.3 |
| Newsprint scan | noise 0.39 premultiply, two linearProgressiveBlurs on the diagonals, a dark tinted vignette |
| Blueprint | Solid #0b2545, gridlines 24 px faint, gridlines 120 px stronger |
| Synthwave floor | dark Solid, gridlines (rotationX -68, perspective 900, offsetY by frame, pink), glow pink |
| Liquid loop | Solid with liquidContours (phase = base + frame / duration: a whole cycle per loop) |
| TV power-off outro | scanlines ramping to 0.58, flickering chromaticAberration, noise by frame, then CSS scale to "1 0.012" and "0 0.012" with a white flash, ending on black |

## HTML-in-canvas with your own shader

When no effect makes the look (a magnifier, a peel, a burn), `<HtmlInCanvas>` accepts `onInit` and `onPaint`:

- `onInit({canvas, element, elementImage, pixelDensity})` runs once: get a WebGL2 context from the OffscreenCanvas
  (`{alpha: true, premultipliedAlpha: true}`), compile, create a texture and a quad, return a cleanup function (or a
  Promise of one, for example after loading an image).
- `onPaint({canvas, elementImage, ...})` runs on every paint: upload with
  `gl.texElementImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, elementImage)`, set uniforms, draw.
  Make it a `useCallback` whose dependencies include every frame-derived value (that is what triggers the repaint).
- Randomness from hashes of the frame number (sin hash, value noise, fbm); the texture is premultiplied, so
  un-premultiply before RGB splits.
- Without `onPaint`/`onInit` the component draws the DOM and runs `effects`; with them the drawing is yours (the
  `effects` then run on your output).
- Sizes are whole CSS pixels; `pixelDensity` above 1 sharpens small type (and costs pixels squared).
- Preview needs Chrome 148+ with `chrome://flags/#canvas-draw-element`; `HtmlInCanvas.isSupported()` tells; the
  render browser (Chrome Headless Shell 149 in 4.0.528) needs no flag.

## CSS techniques used by the css engine

- Grain: an SVG `feTurbulence` (fractal noise, 2 octaves) with its `seed` stepped at 12 Hz, pushed to grey with a
  colour matrix and a steep transfer curve, laid over with `overlay` at 0.2 to 0.35.
- RGB split: an SVG filter that separates the channels with `feColorMatrix`, offsets red and blue with `feOffset`
  and recombines with `screen` blends. Works on any DOM.
- Posterize: `feComponentTransfer` with `type="discrete"` tables.
- Bloom: a second copy of the content with `contrast`, `brightness` and a large `blur`, screened on top (costs a
  second render of the content).
- Halftone in CSS: a white box with `filter: contrast(20+)` holding the greyscale picture multiplied by a radial-dot
  background; then the ink colour with `lighten` and the paper with `multiply`.
- Scanlines: `repeating-linear-gradient` multiplied; roll with `backgroundPosition` from the frame.
- Keep CSS filters off text that is being read when possible (they soften hinting), and never use CSS animations or
  transitions: every value from the frame.
