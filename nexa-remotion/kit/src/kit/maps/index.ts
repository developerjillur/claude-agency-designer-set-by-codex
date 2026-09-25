// The maps module: world and country maps, highlights, zooms, routes and flights, pins, labels, choropleths and
// a globe, drawn from Natural Earth data (world-atlas) with d3-geo. Countries only: pass cities as [lon, lat].
// Import it by path (`./kit/maps`): it bundles about 0.9 MB of map data.
export {WorldMap, type WorldMapProps, type HighlightSpec, type FillSpec} from './WorldMap';
export {MapZoom, type MapZoomProps, type ZoomTarget} from './MapZoom';
export {Globe, type GlobeProps, type GlobeKey} from './Globe';
export {CountryShape, type CountryShapeProps} from './CountryShape';
export {Route, legSchedule, legFrames, routeProgress, followCamera, type RouteProps, type RouteStop, type Leg} from './Route';
export {Pin, pinFrames, type PinProps} from './Pin';
export {GeoLayer, type GeoLayerProps} from './GeoLayer';
export {CountryLabel, CountryLabels, Tag, type CountryLabelProps, type CountryLabelsProps, type LabelStyle, type Side} from './Labels';
export {Choropleth, Legend, type ChoroplethProps, type ChoroplethDatum, type LegendProps, type LegendItem} from './Choropleth';
export {useMap, type MapApi, type Projected} from './context';
export {resolveView, type MapKey, type MapKey as MapCameraKey} from './camera';
export {mapPalette, mix, withAlpha, ramp as colorRamp, contrast, type MapPalette} from './color';
export {countryKey, countryInfo, countryName, allCountries, type CountryRef, type CountryInfo} from './countries';
export {countryFeature, countryAreaKm2, useAtlas10m, type Detail, type LonLat} from './atlas';
export {countryAnchor} from './plate';
export {greatCircle, distanceKm, angleDeg, zoomPath, parallelLine, circleKm, type ProjectionName} from './geo';
