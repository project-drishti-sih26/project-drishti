# 🗺️💻 Roles 3 & 4: Frontend Engineers (Command Center Radar & Dashboard)

## 📌 Ownership
* **Role 3:** Frontend Engineer (Maps & GIS Radar)
* **Role 4:** Frontend Engineer (UI/UX & Dashboard)
* **Stack:** React.js (Vite), Tailwind CSS (Dark Mode), Mapbox GL JS, Recharts, Zustand, Lucide React, jspdf.

---

## 📂 Folder Structure
```
frontend/
├── public/                    # Static assets & icons
├── src/
│   ├── assets/                # Custom map marker SVGs, I4C logos
│   ├── components/
│   │   ├── Map/               # [Owned by Role 3: Maps & GIS]
│   │   │   ├── MapRadar.jsx   # Mapbox GL JS instance with dark theme
│   │   │   ├── Markers.jsx    # Custom animated markers (Red #1, Orange #2-5)
│   │   │   └── H3HexLayer.jsx # Spatial danger zone hex overlays & radius
│   │   └── UI/                # [Owned by Role 4: UI/UX & Dashboard]
│   │       ├── Header.jsx     # Status bar, active alerts, current time
│   │       ├── SidebarLeft.jsx# Case details, victim -> mule transaction flow
│   │       ├── SidebarRight.jsx# Top-5 ranked ATMs list, time window, SHAP reasons
│   │       ├── Alerts.jsx     # Critical flashing alert banners
│   │       └── CaseFlow.jsx   # Visual transaction money trail graph
│   ├── services/              # WebSocket client (ws://) & REST API service
│   ├── store/                 # Zustand store (useAlertStore.js) for live state
│   ├── utils/                 # PDF dispatch generator (jspdf), time helpers
│   ├── App.jsx                # Main 3-column dashboard grid
│   ├── index.css              # Tailwind CSS imports & radar glow animations
│   └── main.jsx               # React entrypoint
├── .env.example               # VITE_MAPBOX_TOKEN, VITE_WS_URL, VITE_API_URL
├── Dockerfile                 # Multi-stage Nginx production build
├── package.json
└── README.md                  # This guide
```

---

## 🎯 Role 3: Maps & GIS Radar Tasks
1. Initialize **Mapbox GL JS** with dark mode styling (`mapbox://styles/mapbox/dark-v11`).
2. Implement **`map.flyTo()` dynamic animation** zooming into predicted ATM coordinates immediately when a WebSocket alert arrives.
3. Render custom SVG markers:
   - **Rank #1 ATM:** High-intensity Red pulsing beacon.
   - **Ranks #2–5 ATMs:** Orange/Amber glowing markers.
4. Render spatial candidate zones: H3 hex overlays or radial circles showing travel boundary.

---

## 🎯 Role 4: UI/UX & Dashboard Tasks
1. Build modern 3-column command center layout (Left: Case Flow, Center: Map Radar, Right: Predictions & Time Window).
2. Create **Live Case Flow** showing: `Victim Account -> ₹ Amount -> Mule Account -> Predicted ATM`.
3. Build **Top-5 Ranked Card List** with hover details showing distance, travel time, and SHAP explainability text.
4. **Killer Feature 1:** **"1-Click Export to Police Dispatch PDF"** generates a formatted PDF dispatch with map preview, suspect details, and ranked ATM addresses for field officers.
5. **Killer Feature 2:** **"Human-in-the-Loop"** buttons (`Confirmed Interception` / `False Alarm`) to log operational feedback.
