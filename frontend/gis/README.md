# 🗺️ Role 3: Frontend Engineer (GIS, Maps & Spatial Radar)
**Project Drishti** — Predictive Analytics System for Cybercrime Complaints

---

## 📌 Mission & Architecture Overview

The **Maps & GIS Radar** module provides law-enforcement and cybercrime investigators with an interactive, real-time tactical command center map. It visualizes predicted cash withdrawal locations, danger zones via Uber H3 hexagons, expected withdrawal time windows, and machine-learning explainability factors.

### 🆓 Zero-Cost & Open-Source Mapping Stack
* **Map Engine:** [MapLibre GL JS](https://maplibre.org/) (Open-source WebGL interactive vector mapping fork).
* **Basemap Provider:** [OpenFreeMap](https://openfreemap.org/) using the official Liberty vector style (`https://tiles.openfreemap.org/styles/liberty`).
* **Spatial Binning:** [Uber H3](https://h3geo.org/) (`h3-js`) for hexagonal spatial risk indexing.
* **No Accounts / No Credit Cards / No API Tokens Required:** Completely free, keyless, and open.

### 🏛️ Team Ownership Boundaries
* **Role 3 (Maps & GIS Radar — THIS MODULE):**
  * Owns: MapLibre GL JS map canvas, GIS UI, markers, Uber H3 spatial risk rendering, `map.flyTo()` camera engine, popups, target selection, prediction details HUD, and GIS data normalization.
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
├── MapLibre GL JS Canvas      [PredictionDetailsPanel.jsx]
├── OpenFreeMap Liberty Tiles  [ActiveAlertBanner.jsx]
├── Markers.jsx (DOM Pins)     [MapLegend.jsx]
├── H3HexLayer.jsx (GeoJSON)   
└── map.flyTo() Camera Engine
```

---

## 📂 Folder Structure (`frontend/gis/`)

```
frontend/gis/
├── components/
│   ├── GisDashboard.jsx           # Top-level assembled Command Center HUD
│   ├── MapRadar.jsx               # MapLibre GL JS map instance with OpenFreeMap & flyTo
│   ├── Markers.jsx                # Tactical markers (ATM, Bank Branch, BC Point)
│   ├── TopTargetsPanel.jsx        # Top 5 Predicted Locations ranked list
│   ├── PredictionDetailsPanel.jsx # Target details, cashout window & ML explainability
│   ├── ActiveAlertBanner.jsx      # Live incident HUD alert banner & 1-click focus
│   ├── MapLegend.jsx              # Symbology & threat ranking collapsible legend
│   └── H3HexLayer.jsx             # Real Uber H3 hexagonal polygon rendering & GeoJSON
├── utils/
│   └── dataNormalizer.js          # REST / WebSocket schema normalization utilities
├── mockData.js                    # Fictional spatial locations & multi-alert scenarios (Dev fixture only)
├── index.js                       # Barrel export for all GIS components & utilities
└── README.md                      # Comprehensive documentation & integration guide
```

---

## 📦 Required Dependencies

Install standard open-source GIS libraries:

```bash
npm install maplibre-gl h3-js
```

* `maplibre-gl`: High-performance open-source WebGL vector map rendering.
* `h3-js`: Uber H3 Discrete Global Grid System for spatial risk hexagonal indexing.

---

## 🔑 Configuration & Basemap Setup

* **Basemap Style URL:** `https://tiles.openfreemap.org/styles/liberty`
* **API Keys / Tokens:** **None required!** OpenFreeMap and MapLibre do not require any API token, signup, or card configuration.

---

## 🚀 Key Features Implemented

### 1. Interactive Tactical MapLibre Radar (`MapRadar.jsx`)
* OpenFreeMap vector basemap centered on India (New Delhi default: `[77.2090, 28.6139]`).
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
* Closed GeoJSON linear rings rendered via MapLibre vector polygon layers.
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
* **Expected Cash-Out Window:** Dynamic withdrawal window (e.g. `10–25 mins`).
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
