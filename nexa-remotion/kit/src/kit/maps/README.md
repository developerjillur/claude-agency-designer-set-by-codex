# maps

World and country maps for Remotion 4.0.528, drawn as SVG from Natural Earth data (`world-atlas`) with `d3-geo`:
flat maps with a smooth camera, animated highlights, zooms from the world to a country, great-circle routes with a
plane, pins, country names, choropleths with a legend, a rotating globe and single-country shapes. No map service,
no key, no WebGL: every frame is plain vectors, so renders are sharp at any zoom, deterministic, and need no
`--gl=angle` or `--concurrency=1`.

```tsx
import {WorldMap, MapZoom, Globe, CountryShape, Route, Pin, CountryLabel, CountryLabels, Choropleth, GeoLayer} from './kit/maps';
```

Import it by path (`./kit/maps`): it bundles about 0.9 MB of map data (1:110m and 1:50m). The 1:10m data (3.6 MB)
is loaded only when a map zooms in close or asks for it, behind `delayRender`.

## What the data has, and what it does not

- **Countries and territories only** (Natural Earth admin 0: 240 at 1:50m, 255 at 1:10m). There are no states,
  divisions, districts, cities, rivers, roads or place names. Give cities as `[longitude, latitude]` props (Dhaka is
  `[90.4125, 23.8103]`); for divisions or districts you need your own GeoJSON (not part of the kit).
- Countries are found by name, ISO codes or the numeric id: `'Bangladesh'`, `'BGD'`, `'BD'`, `'050'`, `50`, and the
  Bangla name for about 40 countries (`'বাংলাদেশ'`). A typo throws a readable error at once.
- Borders are Natural Earth's de facto lines (world-atlas 2.0.2). Checked in the data: **Crimea is drawn inside
  Russia**; Kashmir is split along the lines of control (Srinagar and Leh in India, Gilgit in Pakistan, Aksai Chin
  in China) with the Siachen Glacier as its own shape; Western Sahara, Taiwan, Kosovo, Northern Cyprus and
  Somaliland are separate shapes. Many governments and clients require their official map (India's, Ukraine's):
  for such work supply the client's GeoJSON instead, and never publish a disputed border without checking it.
- Three detail levels: `110m` (small, coarse: thumbnails and globes), `50m` (default), `10m` (close-ups; loaded on
  demand). The `auto` detail of `WorldMap` cross-fades 50m to 10m as the camera zooms in.

## Coordinates and sizes

Places are `[lon, lat]` (x first, like GeoJSON). All sizes and positions given as numbers (widths, heights, a
globe's `x` and `y`, paddings, stroke and font sizes) are px at a 1080 px short side and are multiplied by the stage
`unit`, like the rest of the kit; `Rect` props (`area`, `safe`) are real px, like `useStage().safe`. Colours come from the theme through `mapPalette(theme)` (land is a quiet tint
of the ground, countries are cut apart by lines of the ground colour, the accent is saved for the subject); every
map takes `colors` to override any part of the palette.

---

## WorldMap

A flat world map: ocean, land, borders, graticule; a camera; highlighted countries; per-country fills. Children
(pins, routes, labels, your own overlays via `useMap()`) are drawn on top, in child order.

| Prop | Default | Notes |
|---|---|---|
| `projection` | `'auto'` | natural earth for world views, Mercator once the camera zooms past about 3x (true local shapes); or `naturalEarth1`, `equalEarth`, `mercator`, `equirectangular` |
| `meridian` | `0` | central meridian; `150` to `180` puts the Pacific in the middle |
| `width`, `height` | the frame | map box, px at 1080; position a smaller box with `style={{left, top}}` |
| `camera` | whole world | `MapKey[]`: see below |
| `rho` | `1.2` | how high long pans rise on the zoom path (0.8 flatter, 1.6 higher) |
| `detail` | `'auto'` | `'110m'`, `'50m'`, `'10m'`, or auto (50m, then 10m when zoomed in) |
| `ocean` | `'sphere'` (`'frame'` for mercator and equirectangular) | sphere: the world's outline on the ground; frame: water edge to edge (use it when the camera moves) |
| `antarctica` | `false` | |
| `padding` | `40` | px around the world at zoom 1 |
| `graticule`, `borders`, `coast` | `false`, `true`, `false` | |
| `highlight` | none | a country, a list, or `HighlightSpec[]` |
| `fills` | none | `{[country]: colour or {color, delay, duration}}`: groups of countries, choropleths |
| `intro` | `'none'` | `'fade'` (whole map) or `'sweep'` (countries west to east); `introDuration` 36 f, `delay` |
| `colors` | theme | `Partial<MapPalette>` (land, ocean, border, highlight list, tag colours, ramp...) |
| `safe` | frame safe area | where labels and tags stay |

**Camera keys** (`MapKey`): `{at, fit?, points?, bbox?, center?, zoom?, padding?, area?, ease?}`. `fit` is
`'world'` or countries (framed by their main body: France without French Guiana, the US without Alaska);
`points` frames places; `bbox` is `[[west, south], [east, north]]`; `center` with `zoom` (1 = whole world). `area`
is the part of the box to frame into (leave room for a title), `padding` the share kept free on each side (default
0.14; 0.18 for points). Between keys the view travels on the smooth zoom path (van Wijk and Nuij: it zooms out as
far as a long pan needs), eased in and out; repeat a key to hold.

**Highlights** (`HighlightSpec`): `{country, color?, delay?, draw?, fill?, reveal?, outline?, label?, sub?, lang?,
labelStyle?, labelMode?, labelSide?, labelDelay?, out?}`. The outline draws on (`draw` 30 f), the fill spreads from
the heart of the country (`reveal: 'radial'`, or `'fade'`; `fill` 20 f, starting when the outline is 45% done) with
a short brighter bloom that settles, then the label rises. `draw: 0` shows the outline at once, `outline: false`
hides it, `fill: 0` fills at frame 0. Colours default to the theme accent, then accent2.

```tsx
<WorldMap camera={[{at: 0, bbox: [[66, 8], [104, 33]]}]}
  highlight={[{country: 'Bangladesh', delay: 12, label: 'বাংলাদেশ', sub: 'Bangladesh', labelMode: 'callout'}]}>
  <CountryLabels countries={['India', 'Myanmar', 'Nepal', 'Bhutan']} lang="bn" />
</WorldMap>
```

Gotchas: the camera changes only the SVG `viewBox` (paths are projected once per plate and reused), so lines keep
their width (`vector-effect: non-scaling-stroke`) and nothing is re-projected per frame. Frame 0 is composed unless
you ask for an intro. Use `ocean="frame"` when the camera moves around: a sphere edge sweeping through the frame
looks like a seam. A camera key that frames a tiny country stops at 1.5 degrees. Close-ups in a world projection
shear the place (natural earth turns a circle round Dhaka into a tilted 1.22 : 1 ellipse); `auto` switches such
cameras to Mercator, or centre the projection with `meridian`. Holds longer than about 0.7 s want a slow drift: a
last key a little closer (padding 0.12 to 0.09) with `ease: curves.sine`.

## MapZoom

The "from the world down to one place" shot in one line: a `WorldMap` holding on `from`, then travelling to `to`
on the zoom path; when `to` is one country it is highlighted as the camera settles.

| Prop | Default | Notes |
|---|---|---|
| `to` | required | country, countries, `{points}`, `{bbox}` or `{center, zoom}` |
| `from` | `'world'` | same forms |
| `delay` | 0.5 s | hold on `from` |
| `duration` | 2.4 s | the move |
| `padding`, `area`, `ease` | 0.16 | framing of the target |
| `highlightTarget` | `true` | or a partial `HighlightSpec` (label, colour...) |

```tsx
<MapZoom to="Bangladesh" delay={20} duration={90} highlightTarget={{label: true, sub: 'বাংলাদেশ'}}>
  <Pin at={[90.4125, 23.8103]} label="Dhaka" delay={140} />
</MapZoom>
```

Everything else is `WorldMap`'s. A close zoom loads the 10m data (auto detail); keep `detail="auto"`.

## Globe

An orthographic globe that turns to face places, can spin and zoom. Land, borders and graticule are re-projected
each frame and clipped at the horizon; a radial shading, a darker rim and a thin atmosphere give it volume.

| Prop | Default | Notes |
|---|---|---|
| `size` | 82% of the short side | diameter, px at 1080 |
| `x`, `y` | box centre | centre, px at 1080 |
| `keys` | none | `{at, center?: [lon, lat] or country, zoom?, ease?}`; centres travel along the great circle |
| `center`, `zoom` | `[15, 22]`, 1 | when there are no keys |
| `spin` | 0 | degrees per second, eastward |
| `detail` | `'auto'` | 110m, 50m once zoomed in |
| `graticule`, `borders`, `shade`, `glow` | all `true` | |
| `highlight`, `fills`, `colors`, `safe` | | as WorldMap |

```tsx
<Globe keys={[{at: 0, center: [10, 30]}, {at: 70, center: 'Bangladesh', zoom: 1.05}]} highlight={[{country: 'BGD', delay: 60}]}>
  <Route stops={[[90.41, 23.81], {at: [-0.13, 51.51], label: 'London'}]} delay={96} marker="dot" originPin={false} />
  <Pin at={[90.4125, 23.8103]} label="Dhaka" delay={78} side="bottom" />
</Globe>
```

Gotchas: the latitude of `center` tilts the globe (22 degrees looks natural). Pins, tags and labels fade near the
edge and vanish behind it; routes lift off the surface (`lift` 0.2 of the radius) and pass behind the globe. Put
pins after routes so their tags sit on top of the lines.

## CountryShape

One country alone, fitted to a box in an equal-area conic projection centred on it (true shape at any latitude): the
outline draws on, the fill spreads from its heart, the name rises below.

| Prop | Default | Notes |
|---|---|---|
| `country` | required | |
| `width`, `height` | the safe area | px at 1080; position with `style={{left, top}}` |
| `detail` | `'50m'` | `'10m'` for a shape taller than about 500 px |
| `mainland` | `true` | only the main body |
| `scale` | fit | px per degree of latitude: the same value on several shapes compares their sizes truthfully |
| `delay`, `draw`, `fill`, `reveal` | 0, 40 f, 20 f, radial | |
| `color`, `lineColor`, `lineWidth` | accent, derived, 3 | |
| `label`, `sub`, `lang`, `labelSize` | the name, none, en, 64 | Bangla works: `label="বাংলাদেশ"` |
| `neighbours`, `shadow` | `false`, `true` | faint land around it, soft shadow under it |
| `out`, `outAt` | label leaves at the end (default: it stays) | |

```tsx
<CountryShape country="Bangladesh" detail="10m" label="বাংলাদেশ" sub="Bangladesh" neighbours delay={6} />
```

## Route

A trip along great circles, leg after leg: the line draws (solid, dashed or dotted), a plane (or a dot) flies at its
tip turned along the path, pins land at each stop as it arrives. On a flat map the arc gets a little lift (bent the
way the great circle already bends) so short hops read as flights; legs across the date line are drawn without lift.

| Prop | Default | Notes |
|---|---|---|
| `stops` | required | `[lon, lat]` or `{at, label?, sub?, side?}`, two or more |
| `delay`, `legDuration`, `dwell` | 0, from distance, 14 f | legDuration per leg or one number |
| `ease` | ease in-out | takes off, cruises, lands |
| `lift` | 0.14 flat, 0.2 globe | |
| `marker`, `markerSize` | `'plane'`, 46 | `'dot'`, `'none'` |
| `trail`, `width`, `color`, `casing` | solid, 4, accent, true | |
| `ghost` | `false` | the whole route faintly, dotted, before it is flown |
| `pins`, `originPin`, `pinKind`, `pinColor` | true, true, dot | `originPin={false}` when several routes share an origin |
| `out`, `outAt` | stays | |

Helpers: `legSchedule(stops, fps, {delay, legDuration, dwell})` returns each leg's `{start, end, km}` (the same
timing the Route uses), `routeProgress(frame, legs)` gives the km flown so far (for a counter), `legFrames(angle,
fps)` the default leg length (about 1.1 s for a hop, 2.3 s across a continent), `followCamera(stops, legs, {padding,
overview, area, lift})` camera keys that frame each leg and, with `overview`, the whole trip at the end.

```tsx
const legs = legSchedule(trip, fps, {delay: 24, dwell: 30});
<WorldMap camera={followCamera(trip, legs, {overview: 40})} ocean="frame">
  <Route stops={trip} delay={24} dwell={30} ghost />
</WorldMap>
```

Gotchas: pass the same `delay`, `dwell` and `legDuration` to `legSchedule` and to the Route. Tags whose point
leaves the frame hide themselves. For a Pacific trip set `meridian={180}` on the map.

## Pin

A place marker that lands with a short settle, sends one pulse (two rings) as it lands, and opens a label pill.

| Prop | Default | Notes |
|---|---|---|
| `at` | required | `[lon, lat]` |
| `label`, `sub` | none | the pill; `sub` is a second, quieter line |
| `kind` | `'dot'` | `'pin'` (drops in with a ground shadow), `'ring'` (an area of interest) |
| `color`, `size` | accent2, 18 | |
| `pulse` | `'once'` | `'none'`, or `'loop'` (one slow ring every 1.8 s; use sparingly) |
| `side` | `'auto'` | the side with room inside the safe area; flips when the safe area would push it over the pin |
| `delay`, `labelDelay`, `labelSize` | 0, 6, 26 | |
| `out`, `outAt` | leaves at the end of the Sequence (default: it stays) | |

```tsx
<Pin at={[91.7832, 22.3569]} label="Chattogram" sub="চট্টগ্রাম" delay={152} side="right" />
```

## CountryLabel and CountryLabels

Country names at the pole of inaccessibility (the point deepest inside the largest part of the country, not the
centroid, which falls on coasts or outside), with a halo so they read over borders. When the name does not fit
inside, `mode: 'auto'` makes a callout: a leader from the heart of the country to just past its edge, and a tag.

`CountryLabel`: `{country, text?, sub?, lang?, style? ('caps' quiet context, 'title' the subject, 'plain'), mode?,
side?, size?, color?, halo?, delay?, duration?, out?, outAt?, offset?, decideAt?}`.
`CountryLabels`: `{countries?, exclude?, lang?, style?, size?, max? (40), delay?, stagger? (2), out?, outAt?,
decideAt?}`: only names that fit inside their country, biggest first, never overlapping.

```tsx
<CountryLabels delay={40} stagger={1} />
<CountryLabel country="India" lang="bn" delay={120} />
```

Gotchas: inside or callout, the callout side and which names show are decided on one frame (`decideAt`, default the
label's delay) so nothing flips during a camera move. Bangla is never letter-spaced or upper-cased.

## Choropleth and Legend

`Choropleth` = a `WorldMap` whose countries are coloured by a value, revealed west to east (`'sweep'`), low to high
(`'rank'`) or together, with a legend that builds with them.

| Prop | Default | Notes |
|---|---|---|
| `data` | required | `{[country]: number}` or `[{country, value}]` |
| `scale` | `'quantile'` | `'quantize'` (equal steps), `'threshold'` (with `breaks`), `'linear'` (smooth) |
| `classes` | 5 | |
| `ramp` | theme ramp | class colours low to high (or stops to spread) |
| `reveal`, `delay`, `duration` | sweep, 0, 1.6 s | |
| `format` | compact (`2K`, `3.4M`) | legend numbers |
| `legend` | on | `{title, note, position, swatch, delay}`, or `false` |

```tsx
<Choropleth data={fromDhaka} scale="threshold" breaks={[2000, 4000, 6000, 8000]} reveal="rank"
  legend={{title: 'Distance from Dhaka, km', note: 'Great-circle distance'}} />
```

`Legend` alone: `{title?, note?, items: {color, label}[], position?, area?, swatch?, delay?}`.

Gotchas: quantile classes put the same number of countries in each class (good for skewed data); a skewed value
such as area will still paint the map mostly in the top classes: a lighter ramp or a threshold scale helps. The
first class reads `< b1`, the others `b+`.

## GeoLayer

Your own GeoJSON on a map or a globe: a district, a river, a coastline, a study area, a line of latitude. Lines draw
on (cut in lon/lat before projection, at an even ground speed, so the draw stays steady while the camera moves);
areas fill in after them. The kit's data has countries only: this is how anything else gets onto the map.

| Prop | Default | Notes |
|---|---|---|
| `data` | required | any GeoJSON in `[lon, lat]` |
| `stroke`, `strokeWidth`, `dash` | accent, 3, solid | `'dashed'`, `'dotted'` |
| `fill`, `fillOpacity` | none, 0.35 | areas; the fill starts at 70% of the draw |
| `delay`, `draw`, `fillFrames` | 0, 36, 18 | `draw: 0` shows lines at once |
| `head` | false | a bright point leading each line (rivers, tracks) |
| `out`, `outAt` | false | fade at the end |

```tsx
<GeoLayer data={parallelLine(23.4368, 87.2, 94.6)} dash="dashed" head delay={12} />
<GeoLayer data={circleKm([90.4125, 23.8103], 100)} fill={t.colors.accent} fillOpacity={0.18} delay={66} />
```

Gotchas: d3 joins points with great circles, so a line of latitude given by its two ends bows towards the pole: use
`parallelLine` (a point every half degree). Polygons wound the GeoJSON-standard way (counter-clockwise) read as
"the whole Earth except this" in d3: GeoLayer rewinds them, a raw `geoPath` does not. Simplify big files first (a
few thousand points is plenty on screen).

## Your own overlays: useMap()

Inside any map, `useMap()` gives `project([lon, lat], altitude?)` to box px this frame (`{x, y, visible}`),
`projectAt(frame)`, `projection` (this frame's d3 projection straight to box px, for `geoPath(map.projection)(...)`),
`countryBox(country, frame?)`, `pxPerDeg`, `width`, `height`, `safe`, `unit`, `palette` and, on a globe,
`globe: {cx, cy, r, center}`.

```tsx
const Ripple: React.FC<{at: LonLat}> = ({at}) => {
  const map = useMap();
  const p = map.project(at);
  return <svg style={{position: 'absolute', inset: 0}}><circle cx={p.x} cy={p.y} r={30 * map.unit} opacity={p.visible} fill="none" stroke={map.palette.pin} /></svg>;
};
```

## Helpers

`countryKey`, `countryInfo` (name, ISO codes, Bangla name), `countryName(ref, 'bn')`, `allCountries()`,
`countryFeature(ref, detail)`, `countryAreaKm2`, `countryAnchor` (label point and inner radius), `greatCircle`,
`distanceKm`, `angleDeg`, `parallelLine(lat, west, east)`, `circleKm(center, km)`, `zoomPath` (the van Wijk path),
`resolveView`, `mapPalette`, `mix` (OKLab), `withAlpha`, `colorRamp`, `contrast`, `useAtlas10m`; the type
`MapCameraKey` (same as `MapKey`).

## Performance

A world view draws about 240 country paths and their borders; a close view culls to the countries in sight. The
first frame in each render tab builds the plate (about 0.1 s at 50m); later frames only change the viewBox. The globe
re-projects every frame (fast at 110m; 50m once zoomed in). The 10m file is fetched once per tab. Measured: the
8-second world-to-Bangladesh zoom (with the 10m cross-fade, a highlight and two pins) renders at 1080p in about 5 s;
demo contact sheets (12 to 20 frames at half size) take 2 to 3 s.
