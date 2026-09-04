import React, { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { renderCustomMarker } from './Markers.jsx';
import { addH3HexLayers, removeH3HexLayers } from './H3HexLayer.jsx';
import { TopTargetsPanel } from './TopTargetsPanel.jsx';
import { MapLegend } from './MapLegend.jsx';
import { mockLocations, mockActiveAlert } from '../mockData.js';

/**
 * MapRadar Component
 * Live Location Map with MapLibre GL JS + OpenFreeMap.
 * Clean, restrained enterprise styling with flat solid markers and standard grey attribution.
 */
const MAP_STYLES = {
  streets: {
    label: 'Street',
    style: 'https://tiles.openfreemap.org/styles/liberty'
  },
  satellite: {
    label: 'Satellite',
    style: {
      version: 8,
      sources: {
        'esri-satellite': {
          type: 'raster',
          tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
          tileSize: 256,
          attribution: 'Esri World Imagery'
        }
      },
      layers: [
        {
          id: 'esri-satellite-layer',
          type: 'raster',
          source: 'esri-satellite',
          minzoom: 0,
          maxzoom: 19
        }
      ]
    }
  },
  dark: {
    label: 'Dark',
    style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
  }
};

const MapRadar = ({
  locations = mockLocations,
  riskCells = mockActiveAlert.risk_cells,
  selectedLocationId = null,
  onSelectLocation = () => {},
  centerCoordinates = [77.2090, 28.6139], // Default: New Delhi, India
  zoom = 12.5,
  showTargetsPanel = false,
  showLegend = false
}) => {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef(new Map());
  const popupsRef = useRef(new Map());

  const [currentStyleKey, setCurrentStyleKey] = useState('streets');
  const [activeSelectedId, setActiveSelectedId] = useState(selectedLocationId || (locations[0]?.id ?? null));
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  const handleStyleChange = (key) => {
    if (!mapInstanceRef.current || key === currentStyleKey) return;
    setCurrentStyleKey(key);
    const selected = MAP_STYLES[key];
    mapInstanceRef.current.setStyle(selected.style);
  };

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
        pitch: 45,
        bearing: -15,
        speed: 1.2,
        curve: 1.4,
        essential: true
      });

      const popup = popupsRef.current.get(target.id);
      const marker = markersRef.current.get(target.id);
      if (popup && marker) {
        popup.addTo(map);
      }
    }
  }, [onSelectLocation]);

  // Sync external selectedLocationId prop
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
        pitch: 40,
        bearing: -15,
        attributionControl: false
      });

      map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
      map.addControl(new maplibregl.FullscreenControl(), 'top-right');
      map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

      map.on('load', () => {
        setIsMapLoaded(true);
      });

      mapInstanceRef.current = map;
    } catch (err) {
      console.error('[MapRadar] Error initializing map:', err);
    }

    return () => {
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

  // Render Markers and H3 Hex Layers
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();
    popupsRef.current.clear();

    if (!locations || locations.length === 0) return;

    locations.forEach((loc, index) => {
      const rank = loc.rank || index + 1;
      const isSelected = activeSelectedId === loc.id;
      const lng = Number(loc.longitude);
      const lat = Number(loc.latitude);

      if (isNaN(lng) || isNaN(lat)) return;

      const markerEl = renderCustomMarker(loc, rank, isSelected);
      const scorePercent = Math.round((loc.riskScore || loc.score || 0.8) * 100);

      const popupHtml = `
        <div class="p-3 bg-white text-slate-900 rounded-[4px] border border-slate-200 shadow-lg font-sans text-xs min-w-[200px]">
          <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100">
            <span class="px-1.5 py-0.5 rounded-[3px] text-[10px] font-mono font-medium ${
              rank === 1 ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-slate-100 text-slate-700 border border-slate-200'
            }">
              Rank #${rank}
            </span>
            <span class="text-[10px] font-mono text-slate-500 font-normal">ATM Node</span>
          </div>
          <p class="font-medium text-slate-900 text-xs leading-snug">${loc.name || loc.bank_name || 'Target Node'}</p>
          ${loc.address ? `<p class="text-[11px] text-slate-500 mt-1 leading-tight font-normal">${loc.address}</p>` : ''}
          <div class="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between font-mono text-[11px]">
            <span class="text-slate-500">Probability:</span>
            <span class="font-medium ${scorePercent >= 85 ? 'text-rose-700' : 'text-slate-800'}">${scorePercent}%</span>
          </div>
        </div>
      `;

      const popup = new maplibregl.Popup({
        offset: 20,
        closeButton: true,
        closeOnClick: false
      }).setHTML(popupHtml);

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

    const renderHexes = () => {
      try {
        addH3HexLayers(map, riskCells || locations);
      } catch (err) {
        console.warn('[MapRadar] H3 Layer warning:', err);
      }
    };

    if (map.isStyleLoaded()) {
      renderHexes();
    } else {
      map.once('style.load', renderHexes);
    }
  }, [locations, riskCells, activeSelectedId, isMapLoaded, flyToTarget, currentStyleKey]);

  return (
    <div className="relative w-full h-full min-h-[360px] overflow-hidden rounded-[4px] border border-slate-200 bg-slate-100 flex flex-col">
      {/* Restrained Basemap Switcher */}
      <div className="absolute top-2 left-2 z-10 flex items-center bg-white/95 backdrop-blur-sm border border-slate-200 rounded-[3px] p-0.5 shadow-sm gap-0.5 pointer-events-auto">
        {Object.entries(MAP_STYLES).map(([key, item]) => (
          <button
            key={key}
            type="button"
            onClick={() => handleStyleChange(key)}
            className={`px-2 py-0.5 text-[10px] font-mono rounded-[2px] transition-colors cursor-pointer ${
              currentStyleKey === key
                ? 'bg-slate-900 text-white font-medium'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Small muted grey attribution in bottom-left corner */}
      <div className="absolute bottom-2 left-2 z-10 pointer-events-none select-none">
        <span className="text-[10px] text-slate-400 font-normal">
          © OpenFreeMap • MapLibre
        </span>
      </div>

      {showTargetsPanel && locations && locations.length > 0 && (
        <div className="absolute bottom-4 left-3 z-10 max-w-xs pointer-events-auto">
          <TopTargetsPanel
            targets={locations}
            selectedTargetId={activeSelectedId}
            onTargetSelect={flyToTarget}
          />
        </div>
      )}

      {showLegend && (
        <div className="absolute bottom-4 right-14 z-10 pointer-events-auto hidden md:block">
          <MapLegend />
        </div>
      )}

      {/* MapLibre Canvas Container */}
      <div ref={mapContainerRef} className="w-full h-full min-h-[360px] flex-1" />
    </div>
  );
};

export default MapRadar;
