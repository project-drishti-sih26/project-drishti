import React, { useState, useCallback, useMemo } from 'react';
import MapRadar from './MapRadar.jsx';
import TopTargetsPanel from './TopTargetsPanel.jsx';
import PredictionDetailsPanel from './PredictionDetailsPanel.jsx';
import ActiveAlertBanner from './ActiveAlertBanner.jsx';
import MapLegend from './MapLegend.jsx';
import { mockLocations, mockActiveAlert, mockMultipleAlerts } from '../mockData.js';
import { normalizeAlertData } from '../utils/dataNormalizer.js';

/**
 * GisDashboard Component (Role 3 - GIS Radar & Spatial Command Center)
 * Project Drishti - Tactical Predictive Analytics System
 * 
 * Assembles the full investigator GIS command center interface:
 * - Active Incident Alert HUD Banner
 * - Interactive Mapbox GL JS Spatial Radar
 * - Uber H3 Hexagonal Risk Zones (CRITICAL, HIGH, MEDIUM, LOW)
 * - Top Predicted Cashout Locations Panel (#1-#5)
 * - Detailed Prediction & ML Explainability Panel ("Why this location?")
 * - Symbology & Threat Ranking Legend
 * - Alert Switcher for Multi-Alert Simulation / Live Stream Readiness
 */
export const GisDashboard = ({
  initialAlert = mockActiveAlert,
  mapboxToken = import.meta.env?.VITE_MAPBOX_TOKEN || '',
  onTargetSelect = () => {}
}) => {
  // Normalize initial alert or fallback
  const normalizedAlert = useMemo(() => {
    return normalizeAlertData(initialAlert) || normalizeAlertData(mockActiveAlert);
  }, [initialAlert]);

  const [currentAlert, setCurrentAlert] = useState(normalizedAlert);
  const [selectedTargetId, setSelectedTargetId] = useState(
    normalizedAlert?.targets?.[0]?.id || mockLocations[0]?.id
  );
  const [flyToTrigger, setFlyToTrigger] = useState(null);

  // Selected target object resolver
  const selectedTarget = useMemo(() => {
    return (
      currentAlert?.targets?.find((t) => t.id === selectedTargetId) ||
      currentAlert?.targets?.[0] ||
      mockLocations[0]
    );
  }, [currentAlert, selectedTargetId]);

  // Handle selecting a target (from list, marker click, or HUD button)
  const handleSelectTarget = useCallback((target) => {
    if (!target) return;
    setSelectedTargetId(target.id);
    setFlyToTrigger(target);
    onTargetSelect(target);
  }, [onTargetSelect]);

  // Handle focusing on the #1 ranked prime target
  const handleFocusPrimeTarget = useCallback(() => {
    const primeTarget = currentAlert?.targets?.[0] || mockLocations[0];
    if (primeTarget) {
      handleSelectTarget(primeTarget);
    }
  }, [currentAlert, handleSelectTarget]);

  // Handle switching mock alerts for demo/simulation testing
  const handleSwitchAlert = useCallback((alertPayload) => {
    const normalized = normalizeAlertData(alertPayload);
    if (normalized) {
      setCurrentAlert(normalized);
      const topTarget = normalized.targets?.[0];
      if (topTarget) {
        setSelectedTargetId(topTarget.id);
        setFlyToTrigger(topTarget);
      }
    }
  }, []);

  return (
    <div className="w-full h-full min-h-screen bg-slate-950 text-slate-100 font-sans p-3 sm:p-5 flex flex-col gap-3.5">
      {/* Top Header & Tactical Controls */}
      <header className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-mono font-bold text-lg shadow-[0_0_15px_rgba(6,182,212,0.25)]">
            🗺️
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-bold tracking-tight text-white font-mono uppercase">
                GIS Spatio-Temporal Radar
              </h1>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-semibold">
                ROLE 3 • DRISHTI
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Predictive Cashout Interception & Threat Corridor Radar
            </p>
          </div>
        </div>

        {/* Demo Alert Switcher Pill Bar */}
        {mockMultipleAlerts && mockMultipleAlerts.length > 1 && (
          <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-mono">
            <span className="text-[10px] text-slate-500 uppercase px-1.5">Alerts:</span>
            {mockMultipleAlerts.map((alert, idx) => (
              <button
                key={alert.alert_id || idx}
                type="button"
                onClick={() => handleSwitchAlert(alert)}
                className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-all ${
                  currentAlert?.alertId === (alert.alert_id || alert.id)
                    ? 'bg-cyan-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                #{idx + 1} {alert.alert_id}
              </button>
            ))}
          </div>
        )}
      </header>

      {/* Active Incident Alert Banner */}
      <ActiveAlertBanner
        activeAlert={currentAlert}
        onFocusPrimeTarget={handleFocusPrimeTarget}
      />

      {/* Main Command Center Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 flex-1 min-h-[620px]">
        {/* Left Column: Top Predicted Targets & Details (lg: 4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-3.5 order-2 lg:order-1">
          {/* Top 5 Predicted Locations */}
          <TopTargetsPanel
            targets={currentAlert?.targets || mockLocations}
            selectedTargetId={selectedTargetId}
            onTargetSelect={handleSelectTarget}
          />

          {/* Selected Target ML Explainability & Cash-Out Window */}
          <PredictionDetailsPanel
            selectedTarget={selectedTarget}
            activeAlert={currentAlert}
            onFlyTo={handleSelectTarget}
          />
        </div>

        {/* Right / Center Column: Mapbox GL JS Canvas & GIS Radar (lg: 8 cols) */}
        <div className="lg:col-span-8 flex flex-col min-h-[500px] lg:min-h-[620px] relative order-1 lg:order-2">
          <MapRadar
            locations={currentAlert?.targets || mockLocations}
            riskCells={currentAlert?.riskCells}
            selectedLocationId={selectedTargetId}
            onSelectLocation={handleSelectTarget}
            mapboxToken={mapboxToken}
            showTargetsPanel={false} // Shown in the structured sidebar
            showLegend={true}
          />
        </div>
      </div>
    </div>
  );
};

export default GisDashboard;
