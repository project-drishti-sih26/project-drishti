# 🗺️ Role 3: Frontend Engineer (GIS & Spatial Radar)

## 📌 Role Ownership & Mission
* **Role:** Frontend Engineer (Maps, GIS Radar & Spatial Visualizations)
* **Goal:** Deliver the mission-critical spatial command center radar. When a live alert triggers from the backend, the radar dynamically centers and zooms (`map.flyTo`) onto the predicted ATM coordinates, displays Uber H3 hexagonal candidate zones, and renders high-priority pulsing markers.
* **Tech Stack:** React.js, Mapbox GL JS (`mapbox://styles/mapbox/dark-v11`), Uber H3 (geojson/polygons), Tailwind CSS, Lucide React.

---

## 📂 Folder Structure
```
frontend/gis/
├── components/
│   ├── MapRadar.jsx       # Core Mapbox GL JS map instance with dark theme & flyTo
│   ├── Markers.jsx        # Custom pulsing SVG markers (Rank #1 Red, Ranks #2-5 Orange)
│   └── H3HexLayer.jsx     # Uber H3 candidate zone hexagons & search radius circles
├── index.js               # Clean component exports
└── README.md              # Role 3 specification & guide
```

---

## 🎯 Key Deliverables
1. **Dark Mode Mapbox Canvas:**
   - Initialize Mapbox GL JS with `mapbox://styles/mapbox/dark-v11`.
   - Smooth navigation controls (pitch, rotate, bearing).
2. **Dynamic `map.flyTo()` Animation:**
   - Smoothly zoom from city-wide overview down to street-level ATM view (zoom level 14-16) upon receiving new alert.
3. **Pulsing Tactical Markers:**
   - **Rank #1 ATM:** High-intensity Red beacon with radiating radar ping animation.
   - **Ranks #2–5 ATMs:** Amber/Orange glowing pins with ranking badges.
   - Interactive popups showing ATM name, distance (km), estimated arrival time, and confidence score.
4. **Spatial Candidate Overlay:**
   - Render H3 hexagons showing candidate spatial bins.
   - Dynamic buffer circle illustrating suspect travel boundary radius within the predicted time window.

---

## 🔗 Integration Points
* **Inputs (Props / Store):**
  - `alertData`: `{ case_id, mule_account, current_location: [lng, lat], predicted_atms: [{ id, name, lng, lat, rank, travel_time, shap_reasons }], h3_indexes: [] }`
* **Outputs:**
  - `onAtmSelect(atmId)` callback to notify UI/UX dashboard when an officer clicks an ATM marker on the radar.
