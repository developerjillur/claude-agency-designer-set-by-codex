# Geo data and the libraries under the kit

What the map data contains, its quirks, and the parts of d3-geo, topojson-client, polylabel and d3-scale the kit
uses, so you can extend it or write a map by hand. Versions installed with the kit: d3-geo 3.1.1, topojson-client
3.1.0, world-atlas 2.0.2, polylabel 2.1.0, d3-scale 4.0.2 (types for all of them).

## world-atlas 2.0.2 (Natural Earth admin 0, TopoJSON)

| File | Size | Countries | Points | Notes |
|---|---|---|---|---|
| `countries-110m.json` | 108 KB | 177 | about 10,600 | coarse (Bangladesh has 36 points); no Singapore, Bahrain, Malta, Maldives, Mauritius |
| `countries-50m.json` | 756 KB | 241 shapes, 240 keys | about 99,500 | the default (Bangladesh 384 points) |
| `countries-10m.json` | 3.6 MB | 255 | about 545,000 | close-ups (Bangladesh 2,257 points); loaded on demand |
| `land-*.json` | 55 KB to 3.1 MB | land only | | not used by the kit (countries merge to the same land) |

Each file has `objects.countries` (geometries with `id` = ISO 3166 numeric as a 3-digit string, `properties.name`)
and `objects.land`. Quirks:

- Names are Natural Earth's short forms: "United States of America", "Dem. Rep. Congo", "Bosnia and Herz.",
  "Central African Rep.", "Dominican Rep.", "S. Sudan", "W. Sahara", "Solomon Is.", "eSwatini", "Macedonia". The
  kit's lookup accepts these and the common names and ISO codes.
- Id `036` is used twice (Australia and the Ashmore and Cartier Islands); the kit merges them.
- Five shapes have no id: Kosovo, Northern Cyprus, Somaliland, Siachen Glacier and the Australian Indian Ocean
  Territories (the kit keys them `n:` + name). 10m adds 14 more small shapes (Gibraltar, Tuvalu, Guantanamo Bay,
  Baikonur, sovereign base areas, reefs).
- The 10m Maldives contains three tiny rings wound the wrong way; d3 reads each as "the whole Earth except this
  speck", which paints the entire map. The kit drops rings whose spherical area is over half the sphere.
- Borders are de facto. Checked in the data: Crimea (Simferopol) is inside Russia; Srinagar and Leh are in India,
  Gilgit in Pakistan, Aksai Chin in China; the Siachen Glacier is its own shape; Western Sahara, Taiwan, Kosovo,
  Northern Cyprus and Somaliland are separate. Clients in India, Ukraine, Morocco, China and elsewhere may require
  their official depiction: use their GeoJSON on a `GeoLayer` (or a custom build), and say so in the delivery note.
- No cities, states, divisions, rivers, lakes, roads or labels. For those, bring GeoJSON (the client's, or open data
  whose licence you have checked) and draw it with `GeoLayer`.

## Coordinates of common places ([lon, lat], two to four decimals)

Check any coordinate before a close zoom; these are city centres.

| Place | [lon, lat] | Place | [lon, lat] |
|---|---|---|---|
| Dhaka | [90.4125, 23.8103] | Kolkata | [88.3639, 22.5726] |
| Chattogram | [91.7832, 22.3569] | New Delhi | [77.2090, 28.6139] |
| Khulna | [89.5403, 22.8456] | Mumbai | [72.8777, 19.0760] |
| Rajshahi | [88.6042, 24.3745] | Kathmandu | [85.3240, 27.7172] |
| Sylhet | [91.8687, 24.8949] | Colombo | [79.8612, 6.9271] |
| Barishal | [90.3535, 22.7010] | Dubai | [55.2708, 25.2048] |
| Rangpur | [89.2752, 25.7439] | Riyadh | [46.6753, 24.7136] |
| Mymensingh | [90.4203, 24.7471] | Doha | [51.5310, 25.2854] |
| Cox's Bazar | [92.0058, 21.4272] | Kuala Lumpur | [101.6869, 3.1390] |
| Singapore | [103.8198, 1.3521] | Bangkok | [100.5018, 13.7563] |
| Tokyo | [139.6917, 35.6895] | Beijing | [116.4074, 39.9042] |
| London | [-0.1276, 51.5072] | Paris | [2.3522, 48.8566] |
| Rome | [12.4964, 41.9028] | Istanbul | [28.9784, 41.0082] |
| New York | [-74.0060, 40.7128] | Toronto | [-79.3832, 43.6532] |
| Los Angeles | [-118.2437, 34.0522] | Sydney | [151.2093, -33.8688] |
| Cairo | [31.2357, 30.0444] | Nairobi | [36.8219, -1.2921] |

Great-circle distances from these (kit `distanceKm`, mean Earth radius 6,371.0088 km): Dhaka to London about 7,995
km; London to New York about 5,570 km.

## d3-geo essentials

- **Projections**: `geoNaturalEarth1`, `geoEqualEarth`, `geoMercator`, `geoEquirectangular`, `geoOrthographic`,
  `geoConicEqualArea`, `geoAzimuthalEqualArea` and more. Chain: `.rotate([-centreLon, -centreLat, roll])` (the
  point shown in the middle), `.scale(k)`, `.translate([x, y])`, `.fitExtent([[x0, y0], [x1, y1]], object)` (scale and
  translate to fit a GeoJSON object in a box), `.fitSize([w, h], object)`, `.clipAngle(90)` (a globe's visible
  hemisphere), `.clipExtent(box)`, `.precision(px)` (adaptive resampling tolerance, default about 0.7 px; the kit
  uses 0.1 on plates, 0.3 on screen projections), `.parallels([p1, p2])` for conics.
- A projection is a function: `projection([lon, lat])` gives `[x, y]` (or null when clipped); `.invert([x, y])`.
- **`geoPath(projection, context?)`**: `path(object)` returns an SVG path string; with a context (anything with
  `moveTo`, `lineTo`, `closePath`, `arc`, `beginPath`) it draws into it (the kit's Recorder keeps the points).
  `path.bounds(object)`, `path.area`, `path.centroid`, `path.measure` work in screen units; `path.digits(n)` sets the
  decimals in path strings (d3-geo 3.1).
- **Spherical helpers**: `geoDistance(a, b)` (radians), `geoInterpolate(a, b)(t)` (points along the great circle),
  `geoArea` (steradians; 4 pi is the Earth), `geoBounds` (east may be smaller than west across the date line),
  `geoCentroid`, `geoContains(feature, point)`, `geoCircle().center(c).radius(deg)()` (a circle polygon),
  `geoGraticule10()`, `geoRotation(angles)`.
- **Rules that bite**: lines between vertices are great-circle arcs (a two-point parallel bows poleward; densify);
  polygons are spherical and their winding decides inside and outside (d3 wants clockwise outer rings, the GeoJSON
  standard says counter-clockwise: rewind, or the fill covers the world); geometry crossing the date line is cut by
  the projection's clipping (fills close along the cut; draw outlines as lines, not polygons, so the cut does not
  draw a border along the edge).

## topojson-client

- `feature(topology, object)` returns GeoJSON (a Feature or FeatureCollection).
- `mesh(topology, object, filter?)` returns a MultiLineString of arcs; `filter(a, b)` receives the two geometries that
  share an arc (`a === b` for coastlines): `(a, b) => a !== b` gives only borders between countries, drawn once.
- `merge(topology, geometries)` dissolves shapes into one (continents, regions); `neighbors(geometries)` lists
  adjacent shapes.

## polylabel

`polylabel(rings, precision)` returns the pole of inaccessibility `[x, y]` with `.distance` (the radius of the
largest circle inside). Run it on projected or locally scaled coordinates (the kit multiplies longitude by the
cosine of latitude), on the largest polygon of a country; its `distance` tells whether a name fits inside.

## d3-scale for classes

- `scaleQuantile().domain(values).range(colours)`: equal counts per class; `invertExtent(colour)` gives the class
  limits.
- `scaleQuantize().domain([min, max]).range(colours)`: equal ranges; `.nice()` rounds the domain.
- `scaleThreshold().domain(breaks).range(colours)`: n breaks, n + 1 colours.
- `scaleLinear().domain([min, max]).range([0, 1]).clamp(true)`: feed a colour ramp (the kit mixes colours in OKLab so
  steps look even).

## Custom GeoJSON

- Districts, divisions, rivers, study areas: load a GeoJSON file from `public/` inside `delayRender` (or import it:
  `resolveJsonModule` is on), keep it small (simplify with mapshaper before bundling: a video needs a few thousand
  points, not millions), and draw it with `<GeoLayer data={...} />` on a `WorldMap` or `Globe`.
- Order matters for draw-ons: a river should run source to mouth as one LineString; borders should be complete, not
  clipped to the frame.
- A label point for your own polygon: `polylabel` on its largest ring (as above); for lines, a point at 40 to 60% of
  the length.
- Generated shapes: `circleKm(center, km)` (a true circle on the sphere), `parallelLine(lat, west, east)`,
  `greatCircle(a, b, n)`.
