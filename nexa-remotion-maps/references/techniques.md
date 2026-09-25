# Map techniques: the kit's vector maps, and when to reach beyond them

Remotion renders each frame in headless Chrome, many tabs at once, frames out of order. A map technique is good for
video when every frame is a pure function of the frame number, everything it loads is held with `delayRender`, and
nothing shimmers between frames. Five ways to put a map in a Remotion video, from simplest to heaviest.

## Decision table

| Need | Technique | Key | Cost |
|---|---|---|---|
| countries, highlights, routes, pins, globe, choropleth, your own GeoJSON | **the kit's vector maps** (d3-geo + world-atlas, SVG) | none | light; no WebGL |
| a fixed backdrop: satellite photo, a designed map, a client's map | **static image** (`<Img>` or `<CanvasImage>` from `public/`) | none | lightest |
| an illustrated or classic tile look with a moving camera, no library | **hand-laid tiles** (Web Mercator maths, `<Img>` per tile) | depends on the tile source | medium; tile licences |
| streets, place names, satellite or styled basemaps, 3D buildings | **tile renderer** (Mapbox GL, MapLibre GL, MapTiler SDK) + Turf | Mapbox and MapTiler need keys; MapLibre with a free style does not | heavy; WebGL, `--gl=angle`, concurrency 1 |
| terrain and city flythroughs with pitch, heading and bank | **Cesium** (terrain, photorealistic 3D tiles) | MapTiler or Google keys | heaviest |

Start with the kit. Go further only when the brief needs streets, imagery or terrain.

## The kit's vector maps (what `WorldMap`, `Globe` and friends do)

- Data: Natural Earth countries from world-atlas (TopoJSON, 1:110m, 1:50m bundled; 1:10m loaded on demand).
  topojson-client turns it into GeoJSON features and meshes (shared borders drawn once).
- Flat maps: the world is projected once into a plate (the map box at zoom 1). The camera changes the SVG `viewBox`;
  lines keep their width with `vector-effect: non-scaling-stroke`. Chrome redraws the vectors at the new scale each
  frame: sharp at any zoom, no per-frame projection, no tiles to wait for.
- Why not CSS: `transform: scale()` on a map layer rasterises it at its layout size and stretches the pixels (soft
  at 2x, mush at 20x). Why not re-project: 100,000 points (50m) to 545,000 (10m) per frame is slow; the viewBox gives
  the same picture for free.
- Globe: an orthographic projection re-projected every frame (fast at 110m; 50m when big), clipped at the horizon
  by d3 (`clipAngle(90)`).
- Overlays (pins, labels, routes, `GeoLayer`) are drawn in screen space from `useMap().project(...)` or the frame's
  `useMap().projection`, so their sizes stay constant while the map zooms.
- Render: no special flags. `nrk.py render` as for any scene.

## Static image

Use it when the map only gives context and does not move (or moves as a whole picture): export or generate the image
at the final aspect and at least the rendered size (2x for push-ins), put it in `public/`, show it with
`<Img src={staticFile('map.jpg')} />` (or `<CanvasImage>` when you want the `effects` prop), and place labels and
markers as normal elements. Remotion holds the frame until an `<Img>` has loaded. A slow push-in on a large image
(scale at most 1 relative to its pixels) stays sharp. Keep the source's attribution on screen or in the credits.

## Hand-laid tiles (no map library)

The idea behind the Remotion "Watercolor Map" Element, in outline:

1. Project with Web Mercator by hand: `x = (lon + 180) / 360 * 256 * 2^z`, `y` from the Mercator formula with the
   latitude clamped to about 85.05 degrees.
2. Pick the zoom `z` at which the route spans about the frame width in tiles (1920 / 256 = 7.5 tiles).
3. Interpolate the camera centre between origin and destination with an eased `interpolate()`.
4. For the visible viewport, lay out the 256 px tiles as `<Img>` elements (draw them 257 px so no hairline seams
   show between tiles). Remotion waits for each `<Img>`; in the Player, `pauseWhenLoading` pauses instead of
   flickering.
5. Draw the route yourself (a quadratic curve raised by about `min(400, 0.37 * height, 0.35 * distance)` px, with a
   white casing under the coloured line) and markers and labels as normal elements.

Tile sources have terms: OpenStreetMap's own tile servers forbid bulk use (rendering hundreds of frames counts);
many styled tiles need attribution (for example "CC BY 3.0, data OpenStreetMap"). For client work, download the
tiles you use once (where the licence allows) and serve them from `public/`, so a render never depends on a remote
server.

## Tile renderers: Mapbox GL, MapLibre GL, MapTiler SDK

For streets, place names, satellite imagery or 3D buildings. They draw with WebGL and load tiles over the network,
so four rules make them safe in Remotion:

1. **Hold the frame until the map is idle.** Create the map once (a ref guard), with `interactive: false`,
   `fadeDuration: 0` (and `raster-fade-duration: 0` on raster layers), `attributionControl` handled on your own
   overlay, and `preserveDrawingBuffer: true` in the canvas context attributes (without it screenshots come out
   blank). Take a `delayRender` handle in a `useState` initialiser; on `load` add your sources and layers, apply the
   frame-0 view, call `triggerRepaint()` and continue the handle on the next `idle` event. Every later change of
   data or view takes a new handle released on `idle`.
2. **Do not move the live camera every frame.** Per-frame `jumpTo()` resamples tiles and imagery differently from
   frame to frame and the whole map shimmers. Instead render a **fixed plate**: the map once, static, at the largest
   zoom any camera key needs, in an oversized container, and move that canvas with CSS `translate` and `scale`
   (scale never above 1, or it softens). Transform every overlay with the same numbers. Keep the plate at most
   4096 px on a side (a common WebGL buffer limit; bigger is silently downsampled): 3840 x 2160 for a 1920 x 1080
   video, about 2700 x 3840 for 1080 x 1920. Centre it on the middle of the route's extent. If the move cannot fit,
   cut to a second plate.
3. **Animate data, not the camera.** Grow a route by setting a sliced line as the source data each frame (Turf
   `lineSliceAlong(line, 0, Math.max(0.001, km))`: a zero-length slice throws), change paint properties (opacity,
   width, colour) from the frame, and wait for `idle` each time.
4. **Render with the GPU and one tab:** `--gl=angle` (or `Config.setChromiumOpenGlRenderer('angle')`) and
   `--concurrency=1` while you validate; raise `timeoutInMilliseconds` (60 to 120 s) and `--timeout` for cold
   tiles.

Library notes: Mapbox needs a token (`accessToken`) and shows attribution; its globe view appears at low zoom and its
standard style has 3D landmark buildings. MapLibre is free; with the bundler, point its worker at a same-origin Blob
that imports the worker file of the same version (`setWorkerUrl`), otherwise the worker path is rewritten and
breaks; for a free demo style there is the MapLibre demo tiles style. MapTiler SDK is MapLibre-based with a key;
strip label and minor border layers on `load` when your own labels tell the story. For annotation stories (a river
drawn, countries lighting up as it reaches them), keep your own GeoJSON (ordered, complete, unclipped borders) for
anything that draws; provider tiles are cut at tile edges and have no start-to-end order.

Geometry with Turf: `greatCircle(from, to, {npoints: 100})` for flight paths (across the date line it returns a
MultiLineString: keep the longest part or unwrap the longitudes), `along` for the current point, `length`,
`bbox`, `booleanPointInPolygon`, `pointToLineDistance`. Coordinates are always `[lon, lat]`. Keep the camera route
separate from the target route (the camera can lead, lag or zoom out) and smooth it so sharp turns do not jolt.

## Cesium (terrain and cities in 3D)

For "flight simulator" shots: a camera flying over terrain (MapTiler terrain and satellite) or through photorealistic
3D city tiles (Google). Turn off Cesium's own render loop and call `viewer.render()` yourself inside a settle loop
until the tiles for the frame are loaded, all inside `delayRender` with long timeouts. Smooth the flight path (for
example a few Chaikin passes), walk it by arc length, aim the camera at a point ahead, bank from the turn rate.
Render a middle frame first as a still, then the whole thing with `--gl=angle --concurrency=1 --timeout=180000`.
Google's photorealistic tiles carry attribution and use limits: read the terms before a client delivery. A slow
camera renders fast (the tiles stay cached).

## Render stability: symptoms and fixes

| Symptom | Cause | Fix |
|---|---|---|
| A vector map looks soft while zooming | the map was scaled with CSS `transform` | animate the viewBox (the kit) or re-project |
| A tile map shimmers during a pan | the live camera moves each frame | fixed plate moved with CSS, scale at most 1 |
| A plate looks soft during a push | plate too small, over 4096 px (downsampled) or scaled above 1 | render it at the largest zoom, within 4096 px |
| Blank or transparent WebGL frames | no `preserveDrawingBuffer`, or no GPU flag | set it; `--gl=angle` |
| Tiles missing or half loaded | frame captured before tiles arrived | wait for `idle` after `triggerRepaint()`; fades at 0 |
| "delayRender timed out" | cold tiles, or a handle never continued | longer timeouts; continue or cancel the handle on every path |
| MapLibre worker fails to load | the bundler rewrote the worker URL | `setWorkerUrl` with a same-origin Blob |
| Turf throws at progress 0 | zero-length `lineSliceAlong` | `Math.max(0.001, km)` |
| A flight path jumps across the map | the great circle crosses the date line | split at the jump (the kit does), or unwrap, or centre the Pacific (`meridian`) |
| A country fill covers the whole map | polygon wound the other way (d3 reads it as the complement) | rewind it (the kit's `GeoLayer` does; world-atlas 10m Maldives slivers are dropped) |
| A line of latitude bows towards the pole | d3 joins points by great circles | add points along it (`parallelLine`) |
| A place looks sheared or a circle is an ellipse | a world projection far from its centre | Mercator for close-ups (`projection="auto"`), or a centred projection |
| Labels pop in and out during a move | fit decided every frame | decide once (`decideAt`) |
| Flicker between frames | `Math.random`, time, CSS animations, map fades | frame-pure values, `random(seed)`, fades at 0 |

## Checking a map render

1. Stills at the settled frames at full size (`nrk.py still`): true shapes, smooth coasts at close zooms, labels
   inside the safe area.
2. A short draft render watched at full speed (`nrk.py render --preset draft`, then `agy-watch-video`) for
   shimmer, pops (detail switching, labels) and camera speed.
3. For tile maps and Cesium, also a render with `--concurrency=1` compared against the normal one: any difference is
   a determinism bug.
