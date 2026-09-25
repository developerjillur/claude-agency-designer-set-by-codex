---
name: nexa-remotion-maps
description: "Map animation for Remotion videos with no map key or tile service: world maps (natural earth, equal earth, Mercator, equirectangular), country highlights that draw and fill, zooms from the world down to a country, great-circle routes and flights with a plane, city pins with labels, country names, choropleths with a legend, a rotating globe with arcs that pass behind it, single-country shapes and your own GeoJSON, drawn from Natural Earth data with d3-geo, themed and sharp at any zoom. Use it for any map, route, travel, 'where is it' or data-by-country shot, Banglish included ('map animation banao', 'Bangladesh highlight koro', 'Dhaka theke London route dekhao'). Part of the nexa-remotion family."
---

# Maps for Remotion

Maps that explain: where a place is, how two places connect, how countries compare. The kit's `maps` module draws
countries from Natural Earth (world-atlas) with d3-geo as SVG, coloured by the theme, so every frame is sharp at any
zoom, deterministic, and renders without WebGL, keys or network. Part of the nexa-remotion family: the director
skill is `nexa-remotion`, the kit lives in `~/.claude/skills/nexa-remotion/kit`, and a project made with
`nrk.py new` imports these parts from `./kit/maps` (by path: the module carries about 0.9 MB of map data).

## Fast path

1. **Name the shot.** World context, a highlighted country, a zoom down to a place, a trip, data by country, a
   globe, one country alone, or your own lines and areas. Pick the component from the table below.
2. **Get the places right.** Countries by name, ISO code or numeric id (`'Bangladesh'`, `'BGD'`, `'050'`, `'বাংলাদেশ'`).
   The data has **countries only**: cities are `[longitude, latitude]` props (see `references/geo-data.md` for
   checked coordinates); districts, rivers or roads need the client's GeoJSON on a `GeoLayer`. Numbers on screen
   (distances, areas) are computed (`distanceKm`, `countryAreaKm2`) or come from the client.
3. **Compose.** One subject per shot, the accent only on it. Leave room for text with the camera `area` (the part of
   the frame to land the subject in). Titles and tags stay in the safe area; the map may bleed.
4. **Time it.** Hold the start 0.5 s, move the camera 2 to 3 s, then outline (1 s), fill (0.7 s), label; routes take
   1.1 to 2.4 s a leg; pins land 8 to 12 frames apart with the label 6 frames after the pin. Hold the settled map at
   least the reading time of its labels.
5. **Check.** `nrk.py stills PROJECT`, then full-size `nrk.py still` on every settled frame: the country's shape
   (true, not sheared), labels not colliding or clipped, tags beside their points, Bangla shaped. On a close zoom
   confirm the fine detail loaded (smooth coasts).
6. **Borders.** If the story touches a disputed area (Kashmir, Crimea, Western Sahara, Taiwan...), check the
   depiction against the client's country before delivery (`references/geo-data.md`).

## Components (from `./kit/maps`)

| Component | Use it for | Key props |
|---|---|---|
| `WorldMap` | any flat map: world, region, country; the base the others sit on | `projection` (auto), `meridian`, `camera` keys, `highlight`, `fills`, `ocean`, `graticule`, `intro`, `detail`, `colors` |
| `MapZoom` | the world-to-place zoom in one line | `to`, `from`, `delay`, `duration`, `padding`, `area`, `highlightTarget` |
| `Globe` | "where on Earth", long flights, a turning planet | `keys` [{at, center, zoom}], `spin`, `size`, `x`, `y`, `highlight`, `graticule`, `shade`, `glow` |
| `CountryShape` | one country alone, drawn on and filled, name below | `country`, `detail`, `scale`, `label`, `sub`, `neighbours`, `width`, `height` |
| `Route` | trips and flights along great circles, several legs | `stops`, `delay`, `legDuration`, `dwell`, `marker`, `trail`, `ghost`, `lift`, `pins` |
| `Pin` | a city or a point with a label pill | `at`, `label`, `sub`, `kind` (dot, pin, ring), `pulse`, `side`, `delay` |
| `CountryLabel`, `CountryLabels` | names inside countries, or a callout | `country`, `style` (caps, title), `mode`, `lang`; `countries`, `max`, `stagger` |
| `Choropleth`, `Legend` | values by country, a legend that builds | `data`, `scale`, `classes`, `breaks`, `ramp`, `reveal`, `legend` |
| `GeoLayer` | your own GeoJSON: districts, rivers, lines of latitude, study areas | `data`, `stroke`, `fill`, `dash`, `draw`, `head` |
| `useMap()` | custom overlays at a place | `project`, `projection`, `countryBox`, `pxPerDeg`, `palette`, `safe` |
| helpers | timing and facts | `legSchedule`, `routeProgress`, `followCamera`, `distanceKm`, `countryAreaKm2`, `countryAnchor`, `parallelLine`, `circleKm`, `countryName(ref, 'bn')` |

Every component reads the theme (`useTheme()`); `colors` overrides any part of the map palette (land, ocean,
border, highlight list, tag colours, choropleth ramp).

## Craft rules

**Projection.** World views: natural earth (the default when the camera stays wide). Area comparisons: equal earth.
Zooms past a continent: Mercator, because it keeps local shapes true; natural earth shears a place far from its
centre (a 100 km circle round Dhaka becomes a 1.22 : 1 ellipse tilted 54 degrees). `projection="auto"` (the default)
picks natural earth for world cameras and Mercator once a key zooms past 3x. Pacific stories: `meridian={150}` to
`180`. "Where on Earth" and flights over 5,000 km: the globe.

**Colour.** Land is a quiet tint of the ground (10 to 20% towards the text colour), borders are lines of the
ground colour, water is lighter than land on light themes and darker on dark ones. The accent goes on the subject
only; at most three highlight colours in one frame. Choropleths: 5 to 7 classes, a sequential ramp (light to dark
on light grounds, dark to bright on dark grounds); reverse it when "near" or "low" is the story; a diverging ramp
only around a meaningful middle (zero, the national average). Text on a highlight picks the higher-contrast of the
theme's text and ground colours.

**Lines.** Borders 1.1 px, highlight outline 2.4 px, routes 4 px, all at 1080 and constant while the camera zooms.
A light casing under a route separates it from the borders.

**Camera.** One camera move per beat. World to country: hold 0.5 s, move 2 to 3 s (60 to 90 frames), ease in-out,
padding 12 to 18% round the subject. Long pans rise on the zoom path (`rho` 1.2); a move of more than about 40x
reads better as two shots. Frame the subject away from the text (`area`), and never pan, zoom and add a label at the
same moment: the label comes after the camera lands.

**Highlights.** Outline draws, fill spreads from the heart of the country (starting when the outline is 45% done),
a short brighter bloom settles, then the name. Each step has its own constant length, however big the country.
Small countries get a callout (a leader from inside to just past the border, a tag outside), which the label does by
itself when the name does not fit.

**Labels.** Context names 17 to 22 px caps in a muted colour; the subject 36 to 44 px; pin tags 26 px; nothing below
16 px at 1080. At most about 40 names on a world map; decide which show on one frame so nothing pops during a move.
Bangla is never upper-cased or letter-spaced (it breaks shaping); `lang="bn"` gives Bangla names for about 40
countries.

**Routes.** Legs last 1.1 to 2.4 s by distance, stops dwell 0.5 to 1 s, the plane is 40 to 50 px, the lift 0.12 to
0.2. A multi-leg trip shows its ghost (the whole route, dotted) and a camera that frames each leg while it flies
(`followCamera`), then the whole trip. A km counter uses tabular figures and the same schedule (`routeProgress`).

**Pins.** One arrival pulse (two rings), not a looping heartbeat. Tags sit on the side with room and flip when the
safe area would push them over their point; a tag whose point leaves the frame hides.

**Globe.** Diameter 70 to 90% of the short side (in 9:16, a big globe low in the frame with text above), tilt 15 to
30 degrees (the latitude of the centre), spin at most 3 degrees a second and only during holds, arcs lift 0.15 to
0.25 of the radius. Put pins after routes so their tags sit on top.

**Honesty.** The kit has countries, not cities or regions; coordinates you type are the facts on screen, so check
them. Natural Earth draws de facto borders (Crimea inside Russia, Kashmir split along the lines of control).

## Recipes

**Where is Bangladesh** (world to country, title room at the top):
```tsx
<WorldMap camera={[{at: 0, fit: 'world', area: {x: 0, y: 150, w: 1920, h: 930}}, {at: 26, fit: 'world', area: {x: 0, y: 150, w: 1920, h: 930}}, {at: 116, fit: 'Bangladesh', padding: 0.12}]}
  highlight={[{country: 'Bangladesh', delay: 84, label: true, sub: 'বাংলাদেশ', labelMode: 'inside'}]}>
  <Pin at={[90.4125, 23.8103]} label="Dhaka" sub="ঢাকা" delay={140} side="right" />
</WorldMap>
```

**The one-liner:** `<MapZoom to="Japan" delay={15} duration={75} highlightTarget={{label: true}} />`

**A country in its region, in Bangla:**
```tsx
<WorldMap camera={[{at: 0, bbox: [[66, 8], [104, 33]], padding: 0.02}]}
  highlight={[{country: 'Bangladesh', delay: 12, label: 'বাংলাদেশ', sub: 'Bangladesh', labelMode: 'callout'}]}>
  <CountryLabels countries={['India', 'Myanmar', 'Nepal', 'Bhutan']} lang="bn" size={22} />
</WorldMap>
```

**A trip with a following camera and a counter:**
```tsx
const opts = {delay: 24, dwell: 30};
const legs = legSchedule(trip, fps, opts);
const km = routeProgress(frame, legs).km;
<WorldMap camera={followCamera(trip, legs, {overview: 40, area: {x: 0, y: 190, w: 1920, h: 890}})} ocean="frame">
  <Route stops={trip} {...opts} ghost />
</WorldMap>
```

**Flights from one city on a globe:**
```tsx
<Globe keys={[{at: 0, center: [10, 30]}, {at: 70, center: [72, 30], zoom: 1.05}]} spin={1.5} highlight={[{country: 'BGD', delay: 60}]}>
  {dests.map((d, i) => <Route key={d.label} stops={[DHAKA, d]} delay={96 + i * 10} marker="dot" originPin={false} />)}
  <Pin at={DHAKA} label="Dhaka" delay={78} side="bottom" />
</Globe>
```

**Data by country** (values computed, so they are true):
```tsx
<Choropleth data={fromDhaka} scale="threshold" breaks={[2000, 4000, 6000, 8000, 10000, 12000]} ramp={[...mapPalette(t).ramp].reverse()}
  reveal="rank" legend={{title: 'Distance from Dhaka, km', note: 'Great-circle distance to the middle of each country'}} />
```

**Sizes compared truthfully:** three `CountryShape`s with the same `scale={78}` (px per degree of latitude).

**Your own lines and areas:** `<GeoLayer data={parallelLine(23.4368, 87.2, 94.6)} dash="dashed" head />` and
`<GeoLayer data={circleKm(DHAKA, 100)} fill={t.colors.accent} fillOpacity={0.18} />`.

## Remotion 4.0.528 facts and traps

- The kit's maps are SVG: no WebGL, so no `--gl=angle`, no `--concurrency=1`, no `preserveDrawingBuffer`. Those rules
  are for tile renderers (Mapbox, MapLibre, MapTiler) and Cesium: see `references/techniques.md`.
- The flat camera changes only the SVG `viewBox` over a plate projected once, so vectors are redrawn sharp every
  frame. Scaling a map with CSS `transform` rasterises it at layout size and blurs it; re-projecting 50m or 10m data
  every frame is slow. Line widths stay constant through `vector-effect: non-scaling-stroke`.
- The 1:10m data (3.6 MB) is a dynamic import held by `useDelayRender()` (4.0.342), created in a `useState`
  initialiser; it loads once per render tab. Every other value is a pure function of the frame.
- d3 joins the points of a line with great circles: a parallel given by its two ends bows towards the pole (use
  `parallelLine`). d3 reads polygons wound the GeoJSON-standard way as "the whole Earth except this"; `GeoLayer`
  rewinds them, raw `geoPath` does not.
- world-atlas quirks the kit handles: id `036` holds Australia and the Ashmore reefs; five shapes have no id
  (Kosovo, Northern Cyprus, Somaliland, Siachen Glacier, Indian Ocean Territories); the 1:10m Maldives has three
  inverted slivers that would paint the whole map (dropped).
- JSON imports need `resolveJsonModule` (the kit's tsconfig has it); world-atlas has no `exports` field, so deep
  imports resolve.
- The theme's fonts carry a Bangla fallback; labels are HTML, so shaping is the browser's (correct for conjuncts).
- `interpolatePaths()` and `<HtmlInCanvasMotionBlur>` are 4.0.529: not used, not needed.

## References

- `references/components.md`: every maps component, prop, default and helper, with the map API for custom overlays.
- `references/cartography.md`: projections, colour, labels, camera choreography, highlight, route and pin timing,
  choropleth classification, 9:16 maps, and the checks before delivery.
- `references/techniques.md`: choosing between the kit's SVG maps, a static image, tile maps (Mapbox, MapLibre,
  MapTiler, hand-laid tiles) and Cesium; the fixed-plate method; render stability; errors and fixes.
- `references/geo-data.md`: d3-geo, topojson-client, world-atlas, polylabel and d3-scale in brief; data quirks;
  disputed borders; custom GeoJSON; checked coordinates for common cities.
