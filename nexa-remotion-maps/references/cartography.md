# Cartography for motion: the decisions that make a map shot look designed

A map in a video is read in two or three seconds, often on a phone, while it moves. Every rule here serves that:
one subject, true shapes, a calm camera, names that land after the move, and colour spent only on the story.

## 1. Which map for which shot

| The story says | Shot | Kit |
|---|---|---|
| "This is where it is" | world to country zoom, or a globe turning to it | `MapZoom`, `WorldMap` camera keys, `Globe` keys |
| "It sits between these neighbours" | a regional map, the subject highlighted, neighbours named quietly | `WorldMap` with a `bbox` key, `highlight`, `CountryLabels` |
| "From here to there" | a route drawn over a following camera, a km counter | `Route`, `followCamera`, `routeProgress` |
| "They reach the whole world" | arcs fanning out from one city on a globe | `Globe` + several `Route`s |
| "Countries compared by a number" | a choropleth with a legend | `Choropleth` |
| "How big it is" | the shape alone, or several at one scale | `CountryShape` (`scale`) |
| "This district, this river, this line" | the client's GeoJSON over the kit's map | `GeoLayer` |
| "Look at this exact street" | not the kit: a tile map or a static image | `techniques.md` |

## 2. Projections

Every flat map distorts; choose which distortion the story can afford.

| Projection | Keeps | Distorts | Use for |
|---|---|---|---|
| natural earth | a pleasant world overall | shapes far from the centre meridian (shear) | world views, world routes |
| equal earth | true areas | shapes near the edges | comparing sizes, per-area data (density) |
| Mercator | true local shapes and angles (conformal) | areas towards the poles (Greenland looks like Africa) | close-ups, regions, cities, zooms past a continent |
| equirectangular | simple grid | shapes stretched east-west at high latitudes | technical plots, a plain look |
| orthographic (globe) | a real view of the Earth | half of it is hidden | "where on Earth", long flights, openers |
| equal-area conic (CountryShape) | true shape and area of one country | the rest of the world | a country alone |

Measured at Dhaka (a 1 degree circle projected): natural earth centred at 0 degrees gives a 1.22 : 1 ellipse tilted
54 degrees; centred at 90 degrees still 1.08 : 1; equal earth 1.38 : 1 at 0 degrees; Mercator 1.01 : 1 anywhere.
Hence `projection="auto"`: natural earth while the camera stays wide, Mercator once a key zooms past 3x. For a Pacific
story, move the seam: `meridian={150}` to `180`.

## 3. Colour

- **Ground, land, water.** Land is a quiet tint of the ground (about 17% towards the text colour on light themes, 20%
  on dark). On light themes the water is lighter than the land (almost white), on dark themes darker. Borders are
  hairlines of the ground colour, so countries read as cut paper. `mapPalette(theme)` does all of this.
- **The accent is the story.** One highlighted subject in the accent; a second in accent2 only when the story has
  two (origin and destination, two rivals); never more than three coloured countries in a frame, except in a
  choropleth.
- **Highlights on dark grounds** want their outline lighter than the fill; on light grounds darker (the kit derives
  it). Text inside a highlight must pass contrast: the kit picks the theme's text or ground colour, whichever
  reads.
- **Choropleths.** Sequential ramps for amounts (light to dark on light grounds, dark to bright on dark grounds).
  Reverse the ramp when small is the story ("near", "cheap"). Diverging ramps only around a meaningful middle
  (zero, an average, 50%). 5 to 7 classes; more cannot be told apart in two seconds. Missing data stays land-grey
  and the legend note says so.
- **Pins and routes** take accent2 or the accent; pins need a ring in the ground colour (or white) to stand off the
  land.

## 4. Classifying data

| Scale | Classes | When |
|---|---|---|
| quantile | same number of countries per class | skewed data (population, GDP, area); every class shows up |
| quantize | equal value ranges | evenly spread data; ranges are easy to read |
| threshold | your breaks | round numbers the audience knows (2,000 km, 4,000 km...), official bands |
| linear | smooth ramp | when an exact shade matters less than the gradient (distance fields) |

Legend: title with the unit ("Distance from Dhaka, km"), the first class as `< b1`, the others `b+`, compact
numbers (`2K`, `3.4M`), a one-line source note. Place it in the safe area on an empty sea (bottom-left for world
maps). Reveal: `sweep` (west to east) for a world tour, `rank` (low to high) when order is the story (distance rings
out from a city), `together` for a quick change of state. Give the viewer at least the reading time of the legend
after the last class arrives.

## 5. Labels

- **Hierarchy.** Context names small (17 to 22 px), tracked capitals, muted; the subject 36 to 44 px in the display
  face; pin tags 26 px; nothing below 16 px at 1080 (the phone floor). Big countries only on a world map (the kit
  shows a name only where it fits inside the country).
- **Placement.** Names go at the pole of inaccessibility, not the centroid: in the 50m data Croatia's centroid falls
  in Bosnia, Vietnam's in Laos, and those of Indonesia, Japan, the Philippines and Norway in the sea. A name that does
  not fit becomes a callout: a dot inside, a leader to just past the border, the tag outside, on the side with room.
- **Time.** Names arrive after the camera settles, never during a move; decide which names show on one frame. Stagger
  2 to 3 frames, biggest first. Temporary labels leave at the end of their beat.
- **Bangla.** Never upper-case or letter-space Bangla (it breaks conjuncts); give Bangla names their own line under or
  over the English, or use `lang="bn"` for the whole map. The theme stacks carry a Bangla font.
- **Halo.** A halo in the land colour lets small names cross borders; on a highlight, the halo takes the fill colour.

## 6. Camera choreography

| Move | Length at 30 fps | Notes |
|---|---|---|
| hold before a move | 15 to 30 frames | let the viewer find the start |
| world to country | 60 to 90 frames | ease in-out; the zoom path rises for long pans |
| country to neighbouring country | 40 to 60 frames | a flatter path (`rho` 0.8) keeps both in view |
| follow a route leg | the leg's length, arriving at 40% of the leg | the plane leads, the camera follows |
| final overview | 30 to 45 frames | frame the whole trip, then hold |
| globe turn of 90 degrees | 60 to 80 frames | great-circle path between centres |

- One camera move at a time; no zoom, pan and label together. The subject lands in an `area` away from the text.
- Padding 12 to 18% round a country, 18% round points, 2 to 6% for a region box.
- A zoom of more than about 40x in one move reads as a jump cut in the middle; split it (world to region, cut or
  pause, region to city).
- Holds longer than about 0.7 s want some life: a globe `spin` of 1 to 3 degrees a second, a pin pulse, a slow
  camera drift (a later key 3 to 5% closer).

## 7. Highlights, pins, routes: timing

| Element | Default | Range |
|---|---|---|
| highlight outline | 30 frames | 20 to 45; constant per country, never a slice of a longer reveal |
| highlight fill | 20 frames from 45% of the outline | 12 to 30 |
| bloom settle | 16 frames | |
| label after fill | 60% into the fill | |
| pin land | spring, 2 pulse rings 10 frames apart | |
| pin label | 6 frames after the pin | |
| pins in a row | 8 to 12 frames apart | in reading or story order |
| route leg | 0.9 s + 1.4 s x sqrt(angle / 90) | 1.1 s (a hop) to 2.3 s (a continent) |
| dwell at a stop | 14 frames | 0.5 to 1 s |
| plane | 46 px, fades in over 8% of the leg | 40 to 50 px |
| counter | follows the plane (`routeProgress`) | tabular figures, colour change on arrival |

Draw direction carries meaning: rivers source to mouth, routes origin to destination, borders all at once (rings
drawn in parallel, so islands finish with the mainland).

## 8. Vertical (9:16) maps

- The safe area is 875 px wide from x 65 and 978 px tall from y 270 (shorts): titles and counters live there.
- A world map is tiny in 9:16; use a globe (70 to 95% of the width, placed low so its upper half, with the story,
  sits in the safe area) or a regional map framed into the safe area with `area`.
- Keep pins and tags in the upper two thirds; the bottom 670 px are under the platform's captions and buttons.
- Routes that run east-west suit 16:9; in 9:16 turn the globe so the route runs across its upper face.

## 9. Honesty and checks before delivery

- The data holds countries only. City coordinates you type are facts: check them (a close zoom shows a wrong city
  at once). Numbers come from the client or are computed from the data (`distanceKm`, `countryAreaKm2`) and the
  on-screen note says how.
- Borders are de facto (Natural Earth): Crimea inside Russia, Kashmir split, Western Sahara, Taiwan, Kosovo,
  Northern Cyprus and Somaliland drawn apart. Ask before showing a disputed area; use the client's official GeoJSON
  when their country requires it.
- Shapes: at the final frame of every zoom, is the subject's shape true (Mercator or a centred projection)?
- Detail: at close zooms, are the coasts smooth (10m loaded)? A crude polygon means the fine data did not load.
- Labels: none clipped, none overlapping, none over a busy line, all inside the safe area; Bangla shaped.
- Motion: no label during a camera move; holds long enough to read; the last frame settled.
