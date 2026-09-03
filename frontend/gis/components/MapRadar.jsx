import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { renderCustomMarker } from './Markers';
import { addH3HexLayers } from './H3HexLayer';

/**
 * MapRadar Component (Role 3 - GIS)
 * Renders the tactical dark mode Mapbox radar for Project Drishti.
 * Handles flyTo animations on incoming alerts and overlays candidate ATMs.
 */
const MapRadar = ({
  predictedAtms = [],
  selectedAtmId = null,
  onSelectAtm = () => {},
  centerCoordinates = [77.209, 28.6139], // Default: New Delhi
  zoom = 12,
  mapboxToken = import.meta.env?.VITE_MAPBOX_TOKEN || ''
}) => {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapboxToken) {
      mapboxgl.accessToken = mapboxToken;
    }

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: centerCoordinates,
      zoom: zoom,
      pitch: 45, // 3D perspective for command center feel
      bearing: -17.6
    });

    map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), 'top-right');
    mapInstanceRef.current = map;

    return () => {
      map.remove();
    };
  }, []);

  // Update markers and trigger flyTo whenever predicted ATMs update
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    if (!predictedAtms || predictedAtms.length === 0) return;

    // Add new markers
    predictedAtms.forEach((atm, index) => {
      const rank = index + 1;
      const markerEl = renderCustomMarker(atm, rank, selectedAtmId === atm.id);

      markerEl.addEventListener('click', () => {
        onSelectAtm(atm);
      });

      const popup = new mapboxgl.Popup({ offset: 25, closeButton: false }).setHTML(`
        <div class="p-2 bg-slate-900 text-white rounded border border-red-500/40 text-xs">
          <p class="font-bold text-red-400">#${rank} ATM: ${atm.name || 'Candidate ATM'}</p>
          <p class="text-slate-300 mt-1">Travel Time: ~${atm.travel_time || '15-20'} mins</p>
          <p class="text-slate-400">Confidence: ${((atm.score || 0.85) * 100).toFixed(0)}%</p>
        </div>
      `);

      const marker = new mapboxgl.Marker({ element: markerEl })
        .setLngLat([atm.longitude, atm.latitude])
        .setPopup(popup)
        .addTo(map);

      markersRef.current.push(marker);
    });

    // Fly to #1 Ranked ATM
    const topAtm = predictedAtms[0];
    if (topAtm && topAtm.longitude && topAtm.latitude) {
      map.flyTo({
        center: [topAtm.longitude, topAtm.latitude],
        zoom: 14.5,
        speed: 1.2,
        curve: 1.4,
        essential: true
      });
    }

    // Add H3 Hexagonal candidate zones if map is loaded
    if (map.isStyleLoaded()) {
      addH3HexLayers(map, predictedAtms);
    } else {
      map.once('style.load', () => addH3HexLayers(map, predictedAtms));
    }
  }, [predictedAtms, selectedAtmId]);

  return (
    <div className="relative w-full h-full min-h-[500px] overflow-hidden rounded-xl border border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.15)] bg-slate-950">
      {/* Radar HUD overlay watermark */}
      <div className="absolute top-4 left-4 z-10 pointer-events-none flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-md border border-cyan-500/40">
        <div className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
        <span className="text-xs font-mono font-semibold tracking-wider text-cyan-400">
          SPATIO-TEMPORAL RADAR ACTIVE
        </span>
      </div>

      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};

export default MapRadar;
