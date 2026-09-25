# Scene craft: making 3D look designed

The numbers the kit's defaults are built on, and the choices that separate a product film from a tech demo.

## Units and framing

- One world unit = 200 px at a 1080 px short side. Scene3D sets the camera so the frame's short side is 5.4 units at
  the target, in 16:9, 9:16, 4:5 and 1:1 alike, so a 3.2-unit phone is 640 px tall in every format.
- Size things in "px at 1080" and convert with `useScene3D().px(n)` at the base camera. The visible frame and the
  safe area on the target plane are in `useScene3D().visible` and `.safe`.
- Put type and key graphics inside the safe area. In 9:16 the bottom 950 px or so and the right rail are covered by
  platform UI: stack copy at the top and the product in the middle.
- To place a product right of centre with copy on the left, aim the camera left of it (`target: [-2, 0, 0]`)
  instead of moving the product sideways: the product stays square to the lens.

## Camera language

| Preset | Angles (azimuth, elevation), lens | Use |
|---|---|---|
| `front` | 0, 0; 30 degrees | type, UI cards, charts seen straight on |
| `hero` | 24, 12; 30 | product hero: the classic three-quarter view from a little above |
| `low` | 14, -10; 34 | heroic, monumental (titles, launches) |
| `top` | 0, 55; 30 | flat lays, maps, tabletops |
| `side` | 62, 6; 30 | profile of a device, thickness |
| `close` | 16, 8; 28, 0.7 distance | details |
| `wide` | 0, 8; 45, 1.35 distance | environments, many objects, stronger perspective |

- A long lens (28 to 35 degrees) flattens and flatters products; wide lenses (45+) exaggerate depth and suit
  particles and flythroughs.
- Moves: one camera move per shot. Orbit 20 to 40 degrees over 3 to 6 s for a product; dolly in 10 to 20% for
  emphasis; a slow truck (0.5 to 1 unit) across floating cards for parallax. Ease in-out for moves that start and
  stop in shot, a sine for a gentle drift, `'glide'` through keys when the camera must not stop.
- Add 4 to 8 px of handheld drift (`CameraPath handheld`) to anything held longer than 3 s; keep it at 0 for UI.
- Roll only for energy (a 3 to 6 degree roll on a trailer title), never on product shots.
- Write moves that must work in several formats with orbit angles, `dolly` (a multiple of the base distance) and
  `shift` (a slide in the image plane): the base distance changes with the aspect ratio (10.1 units in 16:9 at 30
  degrees, 17.9 in 9:16), so absolute camera positions tuned in one format are wrong in the other.

## Light

| Rig | Setup (directional intensities, physical units) | Feel |
|---|---|---|
| `studio` | key 2.3 warm from upper left front, rim 1.7 from behind right, hemisphere fill 0.55, environment 0.8 | clean product and type, the default |
| `soft` | hemisphere 1.0, key 0.9 from above front, weak rim, environment 1.0 | UI, cards, playful scenes: low contrast |
| `dramatic` | hard key 3.4 from the side and above, accent-tinted rim 3.2, fill 0.12, environment 0.28 | dark themes, launches, luxury, trailers |
| `flat` | hemisphere 1.5 plus a soft front light | charts and diagrams: no heavy shading |

- Metals and gloss need something to reflect: an environment is not optional (the procedural `RoomEnvironment`).
- Shadows ground objects. Cheapest and always soft: `ContactShadow` (a blob). Real cast shadows: `Scene3D shadows`
  plus `Floor` (a shadow catcher) and `castShadow` meshes; keep the key high (elevation 40 to 60 degrees) so
  shadows stay short.
- On dark grounds a rim light in the accent colour separates the object from the background.

## Materials that read well (MeshPhysicalMaterial / MeshStandardMaterial)

| Surface | Values |
|---|---|
| Anodised aluminium, titanium | metalness 0.85 to 0.9, roughness 0.3 to 0.4, clearcoat 0.2 |
| Chrome, polished metal type | metalness 1, roughness 0.15 to 0.25, strong environment (envMapIntensity 2 to 2.5) |
| Glossy plastic, enamel | metalness 0, roughness 0.15 to 0.2, clearcoat 1 |
| Matte plastic, paper | metalness 0, roughness 0.7 to 0.9 |
| Glass front of a device | near-black, roughness 0.05 to 0.1, clearcoat 1 (reflections do the work) |
| UI screens, video, brand colours that must be exact | `meshBasicMaterial toneMapped={false}` |

Do not use `meshPhongMaterial` or `meshLambertMaterial` for hero objects: they ignore the environment.

## Colour and tone

- `toneMapping: 'neutral'` (Khronos PBR Neutral) keeps brand colours near their hex values; ACES shifts hues and
  desaturates highlights; AgX is the soft filmic choice for bright scenes.
- Background: a CSS gradient behind a transparent canvas (Scene3D's `'studio'` sweep) looks better and cheaper than
  a lit backdrop, and alpha output stays possible (`background="transparent"`).
- Depth: fog in the ground colour for particles and flythroughs; for products, a darker vignette in the CSS
  background.

## Type in 3D

- 3D type is for one hero word or number (a title, a stat, a logo word), not paragraphs: 2D type is sharper and
  reads faster. Keep supporting copy as 2D over the canvas.
- Extrusion depth 0.15 to 0.3 em; bevel 0.01 to 0.03 em (bigger reads chunkier and catches more light).
- Looks: `duo` (exact face colour, accent sides) for brand work, `metal` on dark grounds, `solid` when the face and
  sides share a colour. View the type from within about 25 degrees of straight on so it stays readable.
- Reveal once, then hold still while it is read (at least `readingFrames(text, fps)`); move the camera, not the
  letters, during the hold.

## Timing

| Move | 30 fps frames |
|---|---|
| Product rise into frame | 30 to 40, ease out |
| Product turn (hero) | the whole shot, in-out, 40 to 60 degrees total |
| Turntable, full turn | 4 to 8 s |
| 3D title reveal per letter | 18 to 26, with 10 to 16 frames spread across the word |
| Card fly-in | 24 to 32 each, 5 to 8 apart |
| Camera move | 60 to 150 |
| Exit | 12 to 18, ease in, ending on the last frame |

## Composition with 2D

- Split the frame: product or scene on one side, 2D headline block (eyebrow, headline, one line) on the other, in
  the safe area. Keep the 3D subject off the text column.
- Stack order: Scene3D first, 2D copy after it (on top). A second Scene3D is a second WebGL context; prefer one
  scene with more objects.
- Particles behind type: keep them low contrast (dust opacity 0.6, bokeh 0.1 to 0.18 alpha) and never animate
  behind a line while it is being read at high contrast.

## Performance budget (a 1080p frame on a Mac with ANGLE)

- Up to about 200 k triangles, 20 to 40 draw calls, 2k shadow map, a few 2k textures: renders in well under a
  second a frame.
- Particles: points are cheap (thousands); instanced meshes a few hundred to a few thousand.
- Text3D: each part is a mesh; a 20-letter title is 20 draw calls, fine.
- Bloom roughly doubles the frame's GPU time; use it on hero shots, not everywhere.
