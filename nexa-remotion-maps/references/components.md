# The maps components, in full

Everything the kit's `maps` module exports, with every prop, its default and what to watch for. Import from
`./kit/maps` in a project (`../kit/maps` from `src/demos` in the kit itself). Numbers for sizes and positions are px
at a 1080 px short side (the kit multiplies them by the stage `unit`); `Rect` props (`area`, `safe`) are real px like
`useStage().safe`; times are frames. Places are `[longitude, latitude]`.

A **country reference** (`CountryRef`) is a name (`'Bangladesh'`, `'United States'`), the name Natural Earth uses
(`'United States of America'`, `'Dem. Rep. Congo'`), an ISO alpha-3 (`'BGD'`) or alpha-2 (`'BD'`) code, the ISO
numeric id as a string or number (`'050'`, `50`), a common alias (`'UK'`, `'UAE'`, `'DRC'`, `'Ivory Coast'`,
`'Turkey'`, `'Burma'`) or, for about 40 countries, the Bangla name (`'বাংলাদেশ'`, `'ভারত'`, `'সৌদি আরব'`). An
unknown reference throws at once with a readable message.

## WorldMap

The flat map and the base for pins, routes, labels and `GeoLayer`s (its children, drawn in child order above the
map). It projects the world once into a "plate" the size of the map box (zoom 1 = the whole world fitted) and moves
the camera by changing the SVG viewBox, so nothing is re-projected per frame and every line is redrawn sharp.

| Prop | Type | Default | What it does |
|---|---|---|---|
| `projection` | `'auto'`, `'naturalEarth1'`, `'equalEarth'`, `'mercator'`, `'equirectangular'` | `'auto'` | auto: natural earth when the camera stays wide, Mercator once a key zooms past 3x |
| `meridian` | number | 0 | central meridian; 150 to 180 centres the Pacific |
| `width`, `height` | px at 1080 | the frame | the map box; place a smaller box with `style={{left, top}}` (real px) |
| `camera` | `MapKey[]` | the whole world | the camera, see below |
| `rho` | number | 1.2 | curvature of the zoom path (how far a long pan zooms out) |
| `detail` | `'auto'`, `'110m'`, `'50m'`, `'10m'` | `'auto'` | auto: 50m, cross-fading to 10m between 34 and 58 screen px per degree |
| `ocean` | `'sphere'`, `'frame'` | sphere (frame for Mercator and equirectangular) | sphere: the world's outline on the ground colour; frame: water edge to edge |
| `antarctica` | boolean | false | |
| `padding` | px | 40 | around the world at zoom 1 |
| `graticule` | boolean | false | 10 degree grid |
| `borders` | boolean | true | lines between countries (each shared border drawn once) |
| `coast` | boolean | false | a line along coasts |
| `highlight` | `CountryRef`, `CountryRef[]`, `HighlightSpec[]` | none | animated highlights, see below |
| `fills` | `Record<CountryRef, string or {color, delay?, duration?}>` | none | per-country colours that fade in (groups, choropleths) |
| `intro` | `'none'`, `'fade'`, `'sweep'` | `'none'` | how the map itself appears: whole map fades, or countries appear west to east |
| `introDuration`, `delay` | frames | 36 at 30 fps, 0 | |
| `colors` | `Partial<MapPalette>` | the theme's | override any map colour |
| `safe` | `Rect` | the frame's safe area (or 5% inside a smaller box) | where tags and callouts are kept |
| `style` | CSS | | on the map box |

### MapKey (the camera)

`{at, fit?, points?, bbox?, center?, zoom?, padding?, area?, ease?}` (exported also as `MapCameraKey`).

- `fit`: `'world'` or one or more countries. Countries are framed by their **main body**: the largest part and the
  parts near it (islands and archipelagos join; far territories such as French Guiana, Alaska, Hawaii, the Canaries
  or Svalbard stay out).
- `points`: frame these places (default padding 0.18). A route leg's arc is framed by `followCamera`.
- `bbox`: `[[west, south], [east, north]]` (east may be smaller than west across the date line).
- `center` + `zoom`: zoom 1 is the whole world; zoom 4 about a continent; 20 to 40 a country like Bangladesh.
- `padding`: share of the area kept free on each side (0.14 for countries, 0 for the world).
- `area`: `{x, y, w, h}` in real box px (like `useStage().safe`), the part of the frame to land the subject in
  (leave room for a title).
- `ease`: the curve of the move that arrives at this key (default ease in-out).

Between keys the view follows the smooth zoom path of van Wijk and Nuij (it zooms out as far as a long pan needs
and back in, at an even perceived speed), eased. Repeat a key on a later frame to hold. The closest framing is
about 1.5 degrees. The first and last keys hold before and after.

### HighlightSpec

| Field | Default | Notes |
|---|---|---|
| `country` | required | |
| `color` | the theme accent, then accent2, a mix, positive, negative | |
| `delay` | 0 | when the outline starts |
| `draw` | 30 at 30 fps | outline draw-on frames; 0 shows the outline at once |
| `outline` | true | false: no outline at all |
| `fill` | 20 at 30 fps | fill frames; starts when the outline is 45% drawn; 0 fills at once (no bloom) |
| `reveal` | `'radial'` | the colour spreads from the heart of the country with a soft edge; `'fade'` |
| `label` | none | true: the country's name; a string: your text |
| `sub` | none | a second line |
| `lang` | `'en'` | `'bn'` for the Bangla name |
| `labelStyle` | `'title'` | `'caps'`, `'plain'` |
| `labelMode` | `'auto'` | `'inside'`, `'callout'`; auto makes a callout when the name does not fit |
| `labelSide` | `'auto'` | callout side |
| `labelDelay` | 60% of the fill | after the fill starts |
| `out` | false | the label leaves at the end of the Sequence (it stays by default, so the last frame is never half-faded) |

The fill blooms (a brighter tint for a moment) and settles; the outline is a darker (light themes) or lighter (dark
themes) shade of the fill. Text inside a highlight takes the higher-contrast colour of the theme's text and ground,
with a halo in the fill colour.

## MapZoom

`WorldMap` minus `camera`, plus:

| Prop | Default | Notes |
|---|---|---|
| `to` | required | `'world'`, a country, countries, `{points}`, `{bbox}` or `{center, zoom}` |
| `from` | `'world'` | same forms |
| `delay` | 0.5 s | hold on `from` |
| `duration` | 2.4 s | the move |
| `padding` | 0.16 | round the target |
| `area` | the box | where the target lands |
| `ease` | ease in-out | |
| `highlightTarget` | true | highlight a single-country target as the camera settles (at 62% of the move); a partial `HighlightSpec` sets its label, colour, timing |

It adds its highlight in front of any `highlight` you pass.

## Globe

| Prop | Default | Notes |
|---|---|---|
| `size` | 82% of the box's short side | diameter |
| `x`, `y` | box centre | centre, px at 1080 |
| `width`, `height` | the frame | box, px at 1080 |
| `keys` | none | `GlobeKey[]`: `{at, center?, zoom?, ease?}`; `center` is `[lon, lat]` or a country (its main body's centroid); centres travel along the great circle, zoom exponentially |
| `center`, `zoom` | `[15, 22]`, 1 | when there are no keys |
| `spin` | 0 | degrees per second added to the longitude (east) |
| `detail` | `'auto'` | 110m, 50m once the globe is larger than about 1,600 px across |
| `graticule`, `borders`, `shade`, `glow` | true | shade: light from the upper left, darker rim, a soft highlight; glow: a thin atmosphere |
| `highlight`, `fills`, `colors`, `safe`, `style`, `children` | | as WorldMap |

Highlights on a globe always use 50m shapes (small countries exist only there). Children get `map.kind ===
'globe'`: `project(c, altitude)` returns `visible` (0 behind, fading near the edge); an altitude above 0 (a fraction
of the radius) is visible outside the disc even when it is behind the centre plane.

## CountryShape

| Prop | Default | Notes |
|---|---|---|
| `country` | required | |
| `width`, `height` | the safe area | px; with both set, the component is a box you place with `style` |
| `detail` | `'50m'` | `'10m'` loads on demand (use it above about 500 px tall) |
| `mainland` | true | only the main body |
| `scale` | fit to the box | px per degree of latitude; the same value on several shapes compares sizes truthfully |
| `delay`, `draw`, `fill` | 0, 40, 20 at 30 fps | fill starts at 55% of the draw |
| `reveal` | `'radial'` | or `'fade'` |
| `color`, `lineColor`, `lineWidth` | accent, derived, 3 | |
| `label` | true | the name below; a string for your text; false for none |
| `sub`, `lang`, `labelSize` | none, en, 64 | |
| `neighbours` | false | the land around it, faint, with its borders and the sea |
| `shadow` | true | |
| `out`, `outAt` | false | the label leaves at the end (it stays by default) |
| `colors` | theme | |

The projection is an equal-area conic centred on the country with standard parallels at one sixth and five sixths of
its latitude range: true shape and true relative area at any latitude.

## Route

| Prop | Default | Notes |
|---|---|---|
| `stops` | required | `[lon, lat]` or `{at, label?, sub?, side?}` |
| `delay` | 0 | first take-off |
| `legDuration` | from distance | number or one per leg: `legFrames(angle, fps)` = 0.9 s + 1.4 s x sqrt(angle / 90 degrees) |
| `dwell` | 14 at 30 fps | frames on the ground at each stop |
| `ease` | ease in-out | along each leg (takes off, cruises, lands) |
| `lift` | 0.14 flat, 0.2 globe | arc height: share of the leg's chord (flat), of the radius (globe) scaled by the leg's length |
| `marker` | `'plane'` | `'dot'` (a dot with a halo), `'none'` |
| `markerSize` | 46 | plane length |
| `trail` | `'solid'` | `'dashed'`, `'dotted'` |
| `ghost` | false | the whole route, faint and dotted, before it is flown |
| `width`, `color`, `casing` | 4, accent, true | casing: a light edge under a solid line |
| `pins`, `originPin`, `pinKind`, `pinColor` | true, true, dot, accent2 | a pin lands at each stop as the plane arrives |
| `out`, `outAt` | false | fade the route out at the end |

On a flat map a leg bends the way its great circle already bends (towards the pole), and a leg across the date line
is drawn in two pieces without lift. On a globe the arc rises off the surface and the part behind the globe is
hidden. The plane fades in over the first 8% of a leg and out over the last 10% as the pin lands.

Helpers:
- `legSchedule(stops, fps, {delay, legDuration, dwell})` returns `Leg[]` `{from, to, start, end, angle, km}`, the
  exact timing the Route uses: give both the same options.
- `routeProgress(frame, legs, ease?)` returns `{leg, t, km}` (km flown so far, for counters).
- `followCamera(stops, legs, {padding, overview, area, lift})` returns camera keys: leg 1 framed at the start, each
  next leg framed from just before the plane lands at the previous stop until 40% into the next leg, and with
  `overview` frames the whole trip at the end. It frames the lifted arc, not only the ends.

## Pin

| Prop | Default | Notes |
|---|---|---|
| `at` | required | |
| `label`, `sub` | none | a pill beside the point |
| `delay` | 0 | |
| `kind` | `'dot'` | `'pin'` (a map pin dropping onto its point with a ground shadow), `'ring'` |
| `color`, `size` | accent2 (or negative), 18 | dot diameter; the pin is 2.2x as tall |
| `pulse` | `'once'` | two rings as it lands; `'loop'` one ring every 1.8 s; `'none'` |
| `side` | `'auto'` | right if there is room in the safe area, else left, else above or below; flips if the safe area would push it over the point |
| `labelDelay`, `labelSize` | 6, 26 | |
| `out`, `outAt` | false | stays by default |

`pinFrames(fps)` is how long a pin needs to land and show its tag (26 frames at 30 fps).

## CountryLabel, CountryLabels, Tag

`CountryLabel` props: `country`; `text` (default the name); `sub`; `lang`; `style` (`'caps'`: 17 px, tracked capitals,
muted, the default for context; `'title'`: 40 px display type, for the subject; `'plain'`: 22 px); `mode` (`'auto'`,
`'inside'`, `'callout'`); `side`; `size`; `color`; `halo`; `delay`; `duration`; `out`; `outAt`; `offset` ([x, y] px
nudge); `decideAt` (the frame whose view decides inside or callout and the side; default the delay).

The anchor is the pole of inaccessibility (the point farthest from the edges) of the country's largest polygon,
computed on 50m data in a local equal-scale frame; `countryAnchor(ref)` returns `{lonlat, radiusDeg}`. Inside
labels have a halo in the land colour (`WebkitTextStroke` painted under the fill). A name "fits" when its estimated
width is under 2.6 times the inner radius (3.6 for `CountryLabels`).

`CountryLabels` props: `countries` (default all), `exclude`, `lang`, `style`, `size`, `max` (40), `delay`, `stagger`
(2 frames, biggest first), `out`, `outAt`, `decideAt`. Without `countries` it shows only names that fit inside their
country; either way it never overlaps two names.

`Tag` (used by pins, routes and callouts): `{x, y, title, sub?, side, gap, p, q, map, size?, accent?}` where `p` and
`q` are entrance and exit progress. Use it for your own labels at a point.

## Choropleth and Legend

`Choropleth` = `WorldMap` (without `fills`) plus:

| Prop | Default | Notes |
|---|---|---|
| `data` | required | `{[country]: number}` or `[{country, value}]`; non-finite values are ignored |
| `scale` | `'quantile'` | `'quantize'` (equal ranges), `'threshold'` (your `breaks`), `'linear'` (smooth ramp) |
| `classes` | 5 | |
| `breaks` | none | threshold limits (n breaks make n + 1 classes) |
| `ramp` | the theme's 3-stop ramp | exactly n colours are used as they are; other lengths are spread across the classes |
| `reveal` | `'sweep'` | west to east; `'rank'` low to high; `'together'` |
| `delay`, `duration` | 0, 1.6 s | the whole reveal; each country takes 12 frames |
| `format` | compact numbers | legend labels (`< 2K`, `2K+`, `4K+`...) |
| `legend` | on | `{title, note, position, area, swatch, delay}` or false |

`Legend` alone: `{title?, note?, items: {color, label}[], position? ('bottom-left'...), area?, swatch? (84), delay?,
out?, outAt?}`; swatches wipe in one after another.

## GeoLayer

| Prop | Default | Notes |
|---|---|---|
| `data` | required | any GeoJSON (Feature, FeatureCollection, Geometry) in `[lon, lat]` |
| `stroke`, `strokeWidth`, `dash` | accent, 3, solid | `'dashed'`, `'dotted'` |
| `fill`, `fillOpacity` | none, 0.35 | areas; fill starts at 70% of the draw |
| `delay`, `draw`, `fillFrames` | 0, 36, 18 | `draw: 0` shows lines at once |
| `head` | false | a bright point leading each line while it draws (rivers, tracks) |
| `out`, `outAt` | false | |

Lines are cut in lon/lat (at an even ground speed) before projection, so a draw-on stays steady while the camera
moves. Polygons wound the GeoJSON-standard way are rewound for d3. Works on flat maps and globes.

## useMap() and the map API

Inside any map: `kind` (`'flat'`, `'globe'`), `width`, `height`, `safe`, `unit`, `palette`, `detail`, `project(c,
altitude?)` to `{x, y, visible}`, `projectAt(frame)`, `projection` (this frame's d3 projection straight to box px:
`geoPath(map.projection)(anyGeoJSON)`), `pxPerDeg`, `countryBox(ref, frame?)` (screen box of a country's main body)
and, on a globe, `globe: {cx, cy, r, center}`.

## Other exports

`countryKey(ref)`, `countryInfo(ref)` (`{key, a3, a2, name, atlasName, nameBn}`), `countryName(ref, lang)`,
`allCountries()`, `countryFeature(ref, detail)`, `countryAreaKm2(ref)`, `countryAnchor(ref)`, `useAtlas10m(needed)`,
`greatCircle(a, b, n)`, `distanceKm(a, b)`, `angleDeg(a, b)`, `zoomPath(viewA, viewB, rho)`, `parallelLine(lat,
west, east, step)`, `circleKm(center, km)`, `resolveView(key, plate, W, H)`, `mapPalette(theme, overrides)`, `mix(a,
b, t)` (OKLab), `withAlpha`, `colorRamp(stops, n)`, `contrast(a, b)`.

### MapPalette

`stage, ocean, land, border, coast, graticule, sphere, label, labelMuted, halo, highlight[], highlightLine, pin,
pinRing, route, plane, tagBg, tagText, tagMuted, ramp [low, mid, high], dark`. Derived from the theme: land 17%
(light) or 20% (dark) from the ground towards the text colour; ocean lighter than the ground on light themes, a 6%
accent tint of it on dark themes; borders in a lighter (light) or darker (dark) ground colour; highlights in accent,
accent2, their mix, positive, negative.
