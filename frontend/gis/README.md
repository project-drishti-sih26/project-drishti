# 🗺️ Role 3: Frontend Engineer (GIS, Maps & Spatial Radar)
**Project Drishti** — Predictive Analytics System for Cybercrime Complaints

---

## 📌 Mission & Architecture Overview

The **Maps & GIS Radar** module provides law-enforcement and cybercrime investigators with an interactive, real-time tactical command center map. It visualizes predicted cash withdrawal locations, danger zones via Uber H3 hexagons, expected withdrawal time windows, and machine-learning explainability factors.

### 🏛️ Team Ownership Boundaries
* **Role 3 (Maps & GIS Radar — THIS MODULE):**
  * Owns: Mapbox GL JS map canvas, GIS UI, markers, Uber H3 spatial risk rendering, `map.flyTo()` camera engine, popups, target selection, prediction details HUD, and GIS data normalization.
  * Does **NOT** own: Master ATM database, distance matrix, simulation scripts, or ML prediction generation.
* **Role 5 (Data Engineer):**
  * Owns: `simulation/` directory (`atms_master.csv`, distance matrix, `run_live_demo.py`, simulation data pipelines, source datasets).

```
Role 5 (Simulation / Data Pipelines)
              ↓
ML Engine / Backend Predictive API (FastAPI / WebSocket)
              ↓
  [dataNormalizer.js] (Role 3 Adapter Boundary)
              ↓
    [GisDashboard.jsx] (Tactical Command Center HUD)
   ┌──────────┴──────────────────────────┐
   ▼                                     ▼
[MapRadar.jsx]                 [TopTargetsPanel.jsx]
├── Mapbox GL JS Canvas        [PredictionDetailsPanel.jsx]
├── Markers.jsx (DOM Pins)     [ActiveAlertBanner.jsx]
├── H3HexLayer.jsx (GeoJSON)   [MapLegend.jsx]
└── map.flyTo() Camera Engine
```

---

## 📂 Folder Structure (`frontend/gis/`)

```
frontend/gis/
├── components/
│   ├── GisDashboard.jsx           # Top-level assembled Command Center HUD
│   ├── MapRadar.jsx               # Mapbox GL JS map instance with camera flyTo engine
│   ├── Markers.jsx                # Tactical markers (ATM, Bank Branch, BC Point)
│   ├── TopTargetsPanel.jsx        # Top 5 Predicted Locations ranked list
│   ├── PredictionDetailsPanel.jsx # Target details, cashout window & ML explainability
│   ├── ActiveAlertBanner.jsx      # Live incident HUD alert banner & 1-click focus
│   ├── MapLegend.jsx              # Symbology & threat ranking collapsible legend
│   └── H3HexLayer.jsx             # Real Uber H3 hexagonal polygon rendering & GeoJSON
├── utils/
│   └── dataNormalizer.js          # REST / WebSocket schema normalization utilities
├── mockData.js                    # Fictional spatial locations & multi-alert scenarios
├── index.js                       # Barrel export for all GIS components & utilities
└── README.md                      # Comprehensive documentation & integration guide
```

---

## 📦 Required Dependencies

The GIS module relies on standard industry GIS & UI libraries:

```bash
npm install mapbox-gl h3-js
```

* `mapbox-gl`: High-performance WebGL vector map rendering.
* `h3-js`: Uber H3 Discrete Global Grid System for spatial risk hexagonal indexing.

---

## 🔑 Environment Configuration

Create a `.env` file in the frontend/root directory:

```env
VITE_MAPBOX_TOKEN=pk.eyJ1IjoieW91ci11c2VybmFtZSIsImEiOiJ5b3VyLXRva2VuIn0...
```

> **Security Note:** The token is read strictly via `import.meta.env.VITE_MAPBOX_TOKEN`. It is never hardcoded. If the token is missing, the component displays an informative banner without crashing.

---

## 🚀 Key Features Implemented

### 1. Interactive Tactical Mapbox Radar (`MapRadar.jsx`)
* Dark theme (`mapbox://styles/mapbox/dark-v11`) centered on India (New Delhi default: `[77.2090, 28.6139]`).
* Full navigation controls: pitch, rotate, zoom, scale, and fullscreen.
* Robust unmount cleanup (`markers.remove()`, `removeH3HexLayers(map)`, `map.remove()`) preventing memory leaks.

### 2. Multi-Type Tactical Markers (`Markers.jsx`)
* Distinguishes cashout node types:
  * **ATM** (`ATM` badge)
  * **Bank Branch** (`BNK` badge)
  * **Banking Correspondent / BC Point** (`BC` badge)
* Threat Ranking Visuals:
  * **Rank #1:** Critical Red beacon with animated radiating radar ping waves.
  * **Rank #2–3:** Glowing Amber high-risk pins.
  * **Rank #4+:** Cyan/Slate secondary monitored nodes.
* Interactive popups with Location name, type, risk score %, rank, address, and ETA.

### 3. Real Uber H3 Hexagonal Risk Layers (`H3HexLayer.jsx`)
* Uses `h3-js` (`cellToBoundary`) to compute real hexagonal boundaries `[[lng, lat], ...]`.
* Closed GeoJSON linear rings rendered via Mapbox vector polygon layers.
* Distinct Risk Tiers:
  * 🔴 **CRITICAL (≥ 90%):** `#ef4444` (24% opacity fill + dashed border)
  * 🟠 **HIGH (75%–89%):** `#f59e0b`
  * 🟡 **MEDIUM (60%–74%):** `#eab308`
  * 🟢 **LOW (< 60%):** `#10b981`
* Dynamic updates via `source.setData()` to avoid re-creating layers on data updates.

### 4. Smooth `map.flyTo()` Camera Navigation
* Selecting any target from the **Top Predicted Locations** list, the **Details Panel**, or clicking a marker smoothly flies the camera to the target coordinates (`zoom: 15.2`, `pitch: 50°`, `bearing: -15°`) and activates the marker popup.

### 5. Selected Target Intelligence HUD (`PredictionDetailsPanel.jsx`)
* Displays Target Details (Name, Type, Address, Rank, Risk %).
* **Expected Cash-Out Window:** Dynamic withdrawal window (e.g. `15–35 mins`).
* **Why This Location?:** ML explainability / SHAP rationale factors.

### 6. Active Alert HUD Banner (`ActiveAlertBanner.jsx`)
* Displays active alert ID, mule account, defrauded amount, and a 1-click `Focus #1 Target` button.

### 7. Data Normalization Utility (`dataNormalizer.js`)
* Normalizes any future REST API or WebSocket payload (`normalizeAlertData`, `normalizeTargetLocation`) into GIS entities, ensuring frontend stability even if the backend contract changes.

---

## 💻 Quick Usage Examples

### Using the Full Assembled Dashboard
```jsx
import React from 'react';
import { GisDashboard, mockActiveAlert } from './gis';

export default function CyberCommandCenter() {
  return (
    <GisDashboard 
      initialAlert={mockActiveAlert}
      onTargetSelect={(target) => console.log('Target selected:', target)}
    />
  );
}
```

### Using Only the Map Radar Component
```jsx
import React from 'react';
import { MapRadar, mockLocations, mockActiveAlert } from './gis';

export default function StandaloneMap() {
  return (
    <div className="w-full h-screen p-4 bg-slate-950">
      <MapRadar
        locations={mockLocations}
        riskCells={mockActiveAlert.risk_cells}
        onSelectLocation={(loc) => console.log('Clicked target:', loc)}
      />
    </div>
  );
}
```

---

## 🔌 Future Backend / WebSocket Integration Guide

When the backend / ML WebSocket service is live:

```javascript
import { normalizeAlertData } from './gis';

// Inside your WebSocket listener or Zustand store:
socket.onmessage = (event) => {
  const rawData = JSON.parse(event.data);
  
  // Cleanly normalize incoming alert:
  const normalizedAlert = normalizeAlertData(rawData);
  
  // Pass directly into <GisDashboard initialAlert={normalizedAlert} />
};
```

---

## 🛠️ Troubleshooting

| Issue | Resolution |
| :--- | :--- |
| **Mapbox token warning banner appears** | Ensure `VITE_MAPBOX_TOKEN` is configured in `.env`. |
| **Markers not rendering** | Verify target objects have valid `latitude` and `longitude` numeric fields. |
| **Hexagons not appearing** | Check that `risk_cells` have valid H3 index strings (e.g. `8860145b23fffff`). |
