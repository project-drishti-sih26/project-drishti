/**
 * H3HexLayer Utility (Role 3 - GIS)
 * Overlays spatial boundary zones and Uber H3 hexagonal bins for candidate cashout hotspots.
 */

export const addH3HexLayers = (map, atms = []) => {
  if (!map || !atms || atms.length === 0) return;

  const sourceId = 'candidate-hotspot-source';
  const layerFillId = 'candidate-hotspot-fill';
  const layerLineId = 'candidate-hotspot-line';

  // Remove existing layers if any
  if (map.getLayer(layerLineId)) map.removeLayer(layerLineId);
  if (map.getLayer(layerFillId)) map.removeLayer(layerFillId);
  if (map.getSource(sourceId)) map.removeSource(sourceId);

  // Generate approximate hexagonal geometry polygons around predicted ATMs
  const features = atms.map((atm) => {
    const lng = atm.longitude;
    const lat = atm.latitude;
    const radius = 0.005; // ~500m bounding polygon
    const points = 6;
    const coordinates = [];

    for (let i = 0; i <= points; i++) {
      const angle = (i * 2 * Math.PI) / points;
      coordinates.push([lng + radius * Math.cos(angle) * 1.3, lat + radius * Math.sin(angle)]);
    }

    return {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [coordinates]
      },
      properties: {
        rank: atm.rank || 1,
        id: atm.id
      }
    };
  });

  map.addSource(sourceId, {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features
    }
  });

  // Hex fill with glowing transparent red/amber
  map.addLayer({
    id: layerFillId,
    type: 'fill',
    source: sourceId,
    paint: {
      'fill-color': [
        'match',
        ['get', 'rank'],
        1,
        '#ef4444',
        '#f59e0b'
      ],
      'fill-opacity': 0.15
    }
  });

  // Hex border outline
  map.addLayer({
    id: layerLineId,
    type: 'line',
    source: sourceId,
    paint: {
      'line-color': [
        'match',
        ['get', 'rank'],
        1,
        '#ef4444',
        '#f59e0b'
      ],
      'line-width': 1.5,
      'line-dasharray': [2, 2]
    }
  });
};
