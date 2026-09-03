import * as h3 from 'h3-js';

/**
 * H3HexLayer Utility (Role 3 - GIS Radar)
 * Project Drishti - Uber H3 Spatial Risk Hexagons Overlay
 * 
 * Supports real H3 hexagonal cell boundary rendering and risk tier color mappings:
 * - CRITICAL: Glowing Red (#ef4444)
 * - HIGH: Glowing Amber (#f59e0b)
 * - MEDIUM: Glowing Yellow (#eab308)
 * - LOW: Glowing Emerald (#10b981)
 */

export const H3_SOURCE_ID = 'candidate-h3-hex-source';
export const H3_FILL_LAYER_ID = 'candidate-h3-hex-fill';
export const H3_LINE_LAYER_ID = 'candidate-h3-hex-line';

/**
 * Resolves risk score or risk tier string to tactical glowing hex color
 * @param {string|number} tierOrScore 
 * @returns {string} Hex color string
 */
export const getRiskTierColor = (tierOrScore) => {
  if (typeof tierOrScore === 'string') {
    const t = tierOrScore.toUpperCase();
    if (t === 'CRITICAL') return '#ef4444'; // Red
    if (t === 'HIGH') return '#f59e0b';     // Amber
    if (t === 'MEDIUM') return '#eab308';   // Yellow
    if (t === 'LOW') return '#10b981';      // Emerald
  }

  const score = Number(tierOrScore) || 0;
  if (score >= 0.90) return '#ef4444'; // Critical (>= 90%)
  if (score >= 0.75) return '#f59e0b'; // High (75% - 89%)
  if (score >= 0.60) return '#eab308'; // Medium (60% - 74%)
  return '#10b981';                    // Low (< 60%)
};

/**
 * Converts an H3 cell index to closed GeoJSON coordinates [[lng, lat], ...]
 * Uses h3-js cellToBoundary (v4) or h3ToGeoBoundary (v3) with fallback.
 * 
 * @param {string} h3Index - Hexagonal H3 index
 * @param {number} [fallbackLat] - Fallback latitude if index resolution fails
 * @param {number} [fallbackLng] - Fallback longitude if index resolution fails
 * @returns {Array<[number, number]>|null} Array of [lng, lat] coordinate pairs
 */
export const getH3BoundaryCoordinates = (h3Index, fallbackLat, fallbackLng) => {
  try {
    let boundary = null;

    // Support h3-js v4 API (cellToBoundary)
    const getBoundary = h3.cellToBoundary || h3["h3ToGeoBoundary"];
    if (typeof getBoundary === 'function' && h3Index) {
      boundary = getBoundary(h3Index, true);
    }

    if (Array.isArray(boundary) && boundary.length >= 3) {
      // Ensure the GeoJSON polygon ring is closed (first point === last point)
      const first = boundary[0];
      const last = boundary[boundary.length - 1];
      if (first[0] !== last[0] || first[1] !== last[1]) {
        boundary.push([first[0], first[1]]);
      }
      return boundary;
    }
  } catch (err) {
    console.warn(`[H3HexLayer] Warning converting H3 index ${h3Index}:`, err?.message || err);
  }

  // Graceful mathematical fallback if h3-js is unavailable or index is invalid
  if (typeof fallbackLat === 'number' && typeof fallbackLng === 'number') {
    const radius = 0.0055;
    const points = 6;
    const fallbackCoords = [];
    for (let i = 0; i <= points; i++) {
      const angle = (i * 2 * Math.PI) / points;
      fallbackCoords.push([
        fallbackLng + radius * Math.cos(angle) * 1.3,
        fallbackLat + radius * Math.sin(angle)
      ]);
    }
    return fallbackCoords;
  }

  return null;
};

/**
 * Builds GeoJSON FeatureCollection from an array of risk cells or target locations.
 * 
 * @param {Array<Object>} items - Array of risk cell objects or location objects
 * @returns {Object} GeoJSON FeatureCollection
 */
export const buildH3GeoJson = (items = []) => {
  const features = [];

  items.forEach((item, idx) => {
    if (!item) return;

    const h3Index = item.h3Index || item.h3_index || null;
    const lat = typeof item.latitude === 'number' ? item.latitude : item.lat;
    const lng = typeof item.longitude === 'number' ? item.longitude : item.lng;

    const coordinates = getH3BoundaryCoordinates(h3Index, lat, lng);
    if (!coordinates || coordinates.length < 4) return;

    const score = Number(item.riskScore ?? item.score ?? 0.75);
    const riskTier = item.riskTier || item.risk_tier || (score >= 0.9 ? 'CRITICAL' : score >= 0.75 ? 'HIGH' : score >= 0.6 ? 'MEDIUM' : 'LOW');
    const color = getRiskTierColor(riskTier);

    features.push({
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [coordinates]
      },
      properties: {
        id: item.id || `h3-${idx}`,
        h3Index: h3Index || `calc-h3-${idx}`,
        riskTier: riskTier,
        riskScore: score,
        scorePercent: Math.round(score * 100),
        description: item.description || item.name || `Risk Zone #${idx + 1}`,
        color: color
      }
    });
  });

  return {
    type: 'FeatureCollection',
    features
  };
};

/**
 * Safely adds or updates H3 Risk Hexagon layers on a MapLibre GL map instance.
 * Avoids duplicate source/layer errors by dynamically updating existing GeoJSON sources.
 * 
 * @param {maplibregl.Map} map - MapLibre GL instance
 * @param {Array<Object>} riskItems - Array of risk cell objects or locations
 */
export const addH3HexLayers = (map, riskItems = []) => {
  if (!map || typeof map.getSource !== 'function') return;

  const geojsonData = buildH3GeoJson(riskItems);
  const existingSource = map.getSource(H3_SOURCE_ID);

  // If source already exists, update data dynamically without tearing down layers
  if (existingSource) {
    existingSource.setData(geojsonData);
    return;
  }

  // If source doesn't exist, safely add source and layers
  try {
    map.addSource(H3_SOURCE_ID, {
      type: 'geojson',
      data: geojsonData
    });

    // Hexagon Glowing Translucent Fill Layer
    if (!map.getLayer(H3_FILL_LAYER_ID)) {
      map.addLayer({
        id: H3_FILL_LAYER_ID,
        type: 'fill',
        source: H3_SOURCE_ID,
        paint: {
          'fill-color': ['get', 'color'],
          'fill-opacity': 0.24
        }
      });
    }

    // Hexagon Perimeter Dashed Line Layer
    if (!map.getLayer(H3_LINE_LAYER_ID)) {
      map.addLayer({
        id: H3_LINE_LAYER_ID,
        type: 'line',
        source: H3_SOURCE_ID,
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 2.0,
          'line-dasharray': [3, 2],
          'line-opacity': 0.85
        }
      });
    }
  } catch (err) {
    console.warn('[H3HexLayer] Error initializing H3 layers on map:', err);
  }
};

/**
 * Cleans up H3 GeoJSON layers and source when the map is unmounted or reset.
 * @param {maplibregl.Map} map - MapLibre GL instance
 */
export const removeH3HexLayers = (map) => {
  if (!map) return;
  try {
    if (map.getLayer && map.getLayer(H3_LINE_LAYER_ID)) {
      map.removeLayer(H3_LINE_LAYER_ID);
    }
    if (map.getLayer && map.getLayer(H3_FILL_LAYER_ID)) {
      map.removeLayer(H3_FILL_LAYER_ID);
    }
    if (map.getSource && map.getSource(H3_SOURCE_ID)) {
      map.removeSource(H3_SOURCE_ID);
    }
  } catch (err) {
    console.warn('[H3HexLayer] Warning during cleanup:', err);
  }
};

export default addH3HexLayers;

