import React, { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { renderCustomMarker } from './Markers.jsx';
import { addH3HexLayers, removeH3HexLayers } from './H3HexLayer.jsx';
import { TopTargetsPanel } from './TopTargetsPanel.jsx';
import { MapLegend } from './MapLegend.jsx';
import { mockLocations, mockActiveAlert } from '../mockData.js';

/**
 * MapRadar Component (Role 3 - GIS Radar)
 * Project Drishti - Tactical Command Center Map
 * 
 * Interactive MapLibre GL JS + OpenFreeMap map visualizing predicted cashout locations,
 * Uber H3 danger hexes, tactical pulsating markers, and flyTo camera zooms.
 * Completely free, keyless, and open-source.
 */
const MapRadar = ({
  locations = mockLocations,
  riskCells = mockActiveAlert.risk_cells,
  selectedLocationId = null,
  onSelectLocation = () => {},
  centerCoordinates = [77.2090, 28.6139], // Default: New Delhi, India
  zoom = 12.5,
  showTargetsPanel = true,
  showLegend = true
}) => {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef(new Map());
  const popupsRef = useRef(new Map());

  const [activeSelectedId, setActiveSelectedId] = useState(selectedLocationId || (locations[0]?.id ?? null));
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  // Handle target flyTo navigation
  const flyToTarget = useCallback((target) => {
    if (!target) return;
    const lng = Number(target.longitude);
    const lat = Number(target.latitude);

    if (isNaN(lng) || isNaN(lat)) {
      console.warn('[MapRadar] Invalid coordinates for target:', target);
      return;
    }

    setActiveSelectedId(target.id);
    onSelectLocation(target);

    const map = mapInstanceRef.current;
    if (map) {
      map.flyTo({
        center: [lng, lat],
        zoom: 15.2,
        pitch: 50,
        bearing: -15,
        speed: 1.2,
        curve: 1.4,
        essential: true
      });

      // Automatically open the popup for the selected marker
      const popup = popupsRef.current.get(target.id);
      const marker = markersRef.current.get(target.id);
      if (popup && marker) {
        popup.addTo(map);
      }
    }
  }, [onSelectLocation]);

  // Sync external selectedLocationId prop and trigger flyTo when selection changes
  useEffect(() => {
    if (selectedLocationId && selectedLocationId !== activeSelectedId) {
      setActiveSelectedId(selectedLocationId);
      const target = locations?.find((l) => l.id === selectedLocationId);
      if (target && isMapLoaded) {
        flyToTarget(target);
      }
    }
  }, [selectedLocationId, locations, activeSelectedId, isMapLoaded, flyToTarget]);

  // Initialize MapLibre Instance with OpenFreeMap Basemap
  useEffect(() => {
    if (!mapContainerRef.current) return;

    let map = null;
    try {
      map = new maplibregl.Map({
        container: mapContainerRef.current,
        style: 'https://tiles.openfreemap.org/styles/liberty',
        center: centerCoordinates,
        zoom: zoom,
        pitch: 45,
        bearing: -17.6,
        attributionControl: false
      });

      // Add zoom and rotation navigation controls
      map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
      map.addControl(new maplibregl.FullscreenControl(), 'top-right');
      map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

      map.on('load', () => {
        setIsMapLoaded(true);
      });

      mapInstanceRef.current = map;
    } catch (err) {
      console.error('[MapRadar] Error initializing MapLibre GL map:', err);
    }

    return () => {
      // Memory cleanup when component is destroyed
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current.clear();
      popupsRef.current.clear();
      removeH3HexLayers(map);
      if (map) {
        map.remove();
      }
      mapInstanceRef.current = null;
    };
  }, []);

  // Render Markers and H3 Hex Layers when data or map loads
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear existing markers from DOM
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();
    popupsRef.current.clear();

    if (!locations || locations.length === 0) return;

    // Render Markers for each location
    locations.forEach((loc, index) => {
      const rank = loc.rank || index + 1;
      const isSelected = activeSelectedId === loc.id;
      const lng = Number(loc.longitude);
      const lat = Number(loc.latitude);

      if (isNaN(lng) || isNaN(lat)) return;

      const markerEl = renderCustomMarker(loc, rank, isSelected);

      const scorePercent = Math.round((loc.riskScore || loc.score || 0.8) * 100);
      const typeLabel = loc.type || 'ATM';

      // Popup formatted as required:
      // Location name, Location type, Risk score, Rank, Expected window
      const popupHtml = `
        <div class="p-3 bg-slate-950 text-slate-100 rounded-lg border border-cyan-500/40 shadow-2xl font-sans text-xs min-w-[200px]">
          <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-800">
            <span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
              rank === 1 ? 'bg-red-500/30 text-red-400 border border-red-500/50' : 'bg-slate-800 text-cyan-300'
            }">
              RANK #${rank}
            </span>
            <span class="text-[10px] font-mono uppercase text-slate-400 font-semibold">${typeLabel}</span>
          </div>
          <p class="font-bold text-slate-100 text-sm leading-snug">${loc.name || 'Target Node'}</p>
          ${loc.address ? `<p class="text-[11px] text-slate-400 mt-1 leading-tight">${loc.address}</p>` : ''}
          <div class="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between font-mono text-[11px]">
            <span class="text-slate-400">Risk Score:</span>
            <span class="font-bold ${scorePercent >= 85 ? 'text-red-400' : 'text-amber-400'}">${scorePercent}%</span>
          </div>
          ${loc.travelTime ? `
            <div class="mt-1 flex items-center justify-between font-mono text-[11px]">
              <span class="text-slate-400">Travel Time:</span>
              <span class="text-cyan-300">~${loc.travelTime}</span>
            </div>
          ` : ''}
          ${loc.expectedWindow ? `
            <div class="mt-1 flex items-center justify-between font-mono text-[11px]">
              <span class="text-slate-400">Window:</span>
              <span class="text-amber-300">${loc.expectedWindow}</span>
            </div>
          ` : ''}
        </div>
      `;

      const popup = new maplibregl.Popup({
        offset: 28,
        closeButton: true,
        closeOnClick: false,
        className: 'tactical-gis-popup'
      }).setHTML(popupHtml);

      // Add click handler to marker
      markerEl.addEventListener('click', (e) => {
        e.stopPropagation();
        flyToTarget(loc);
      });

      const marker = new maplibregl.Marker({
        element: markerEl,
        anchor: 'bottom'
      })
        .setLngLat([lng, lat])
        .setPopup(popup)
        .addTo(map);

      markersRef.current.set(loc.id, marker);
      popupsRef.current.set(loc.id, popup);
    });

    // Update H3 Spatial candidate hex layer with real H3 boundaries
    const renderHexes = () => {
      try {
        addH3HexLayers(map, riskCells || locations);
      } catch (err) {
        console.warn('[MapRadar] H3 Layer render warning:', err);
      }
    };

    if (map.isStyleLoaded()) {
      renderHexes();
    } else {
      map.once('style.load', renderHexes);
    }
  }, [locations, riskCells, activeSelectedId, isMapLoaded, flyToTarget]);

  return (
    <div className="relative w-full h-full min-h-[600px] overflow-hidden rounded-2xl border border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.15)] bg-slate-950 flex flex-col">
      {/* Tactical HUD Header Bar */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap items-center gap-2 pointer-events-auto">
        <div className="flex items-center gap-2 bg-slate-900/90 backdrop-blur-md px-3.5 py-1.5 rounded-lg border border-cyan-500/40 shadow-lg">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
          <span className="text-xs font-mono font-bold tracking-widest text-cyan-300 uppercase">
            GIS SPATIO-TEMPORAL RADAR
          </span>
          <span className="hidden sm:inline-block text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/40 font-semibold">
            OPENFREEMAP LIBERTY
          </span>
        </div>
      </div>

      {/* Floating Top Predicted Targets Panel (Left / Center) */}
      {showTargetsPanel && locations && locations.length > 0 && (
        <div className="absolute bottom-4 left-3 z-10 max-w-xs sm:max-w-sm pointer-events-auto">
          <TopTargetsPanel
            targets={locations}
            selectedTargetId={activeSelectedId}
            onTargetSelect={flyToTarget}
          />
        </div>
      )}

      {/* Floating Tactical Legend (Bottom-Right) */}
      {showLegend && (
        <div className="absolute bottom-4 right-14 z-10 pointer-events-auto hidden md:block">
          <MapLegend />
        </div>
      )}

      {/* MapLibre Canvas Container */}
      <div ref={mapContainerRef} className="w-full h-full min-h-[600px] flex-1" />
    </div>
  );
};

export default MapRadar;

