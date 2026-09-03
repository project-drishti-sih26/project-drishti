# 🗺️💻 Roles 3 & 4: Frontend Engineers (Command Center Radar & Dashboard)

## 📌 Ownership
* **Role 3:** Frontend Engineer (Maps & GIS Radar) -> Directory: [`frontend/gis/`](./gis/)
* **Role 4:** Frontend Engineer (UI/UX & Dashboard) -> Directory: [`frontend/ui_ux/`](./ui_ux/)
* **Tech Stack:** React.js (Vite), Tailwind CSS (Dark Mode), Mapbox GL JS, Recharts, Zustand, Lucide React, jspdf.

---

## 📂 Folder Structure
```
frontend/
├── gis/                           # 🗺️ [Role 3: Maps, GIS & Spatial Radar]
│   ├── components/
│   │   ├── MapRadar.jsx           # Mapbox GL JS instance with dark theme & flyTo
│   │   ├── Markers.jsx            # Custom animated markers (Red #1 beacon, Orange #2-5)
│   │   └── H3HexLayer.jsx         # Uber H3 candidate zone hex overlays & radius
│   ├── index.js                   # GIS exports
│   └── README.md                  # Role 3 guide & setup
│
├── ui_ux/                         # 💻 [Role 4: UI/UX & Dashboard Layout]
│   ├── components/
│   │   ├── Header.jsx             # Status bar, I4C branding, active alerts, live clock
│   │   ├── SidebarLeft.jsx        # Case details, victim -> mule transaction flow
│   │   ├── SidebarRight.jsx       # Top-5 ranked ATMs list, time countdown, SHAP reasons
│   │   ├── Alerts.jsx             # Critical flashing alert banners (> ₹50,000)
│   │   ├── CaseFlow.jsx           # Visual money trail flow graph
│   │   ├── PoliceDispatchModal.jsx# 1-Click Export to Police Dispatch PDF
│   │   └── FeedbackActions.jsx    # Human-in-the-Loop buttons (Confirmed / False Alarm)
│   ├── index.js                   # UI/UX exports
│   └── README.md                  # Role 4 guide & setup
│
├── public/                        # Static assets & icons
├── src/                           # Common shared application root
│   ├── assets/                    # Custom map marker SVGs, I4C logos
│   ├── services/                  # WebSocket client (ws://) & REST API service
│   ├── store/                     # Zustand store (useAlertStore.js) for live state
│   ├── utils/                     # Formatters & helper utilities
│   ├── App.jsx                    # Assembled 3-column dashboard grid
│   ├── index.css                  # Tailwind CSS imports & radar animations
│   └── main.jsx                   # React entrypoint
├── .env.example                   # VITE_MAPBOX_TOKEN, VITE_WS_URL, VITE_API_URL
├── Dockerfile                     # Multi-stage Nginx production build
├── package.json
└── README.md                      # This guide
```

---

## 🎯 Role 3: Maps & GIS Radar Tasks (`frontend/gis/`)
1. Initialize **Mapbox GL JS** with dark mode styling (`mapbox://styles/mapbox/dark-v11`).
2. Implement **`map.flyTo()` dynamic animation** zooming into predicted ATM coordinates immediately when a WebSocket alert arrives.
3. Render custom SVG markers:
   - **Rank #1 ATM:** High-intensity Red pulsing beacon.
   - **Ranks #2–5 ATMs:** Orange/Amber glowing markers.
4. Render spatial candidate zones: H3 hex overlays or radial circles showing travel boundary.

---

## 🎯 Role 4: UI/UX & Dashboard Tasks (`frontend/ui_ux/`)
1. Build modern 3-column command center layout (Left: Case Flow, Center: Map Radar, Right: Predictions & Time Window).
2. Create **Live Case Flow** showing: `Victim Account -> ₹ Amount -> Mule Account -> Predicted ATM`.
3. Build **Top-5 Ranked Card List** with hover details showing distance, travel time, and SHAP explainability text.
4. **Killer Feature 1:** **"1-Click Export to Police Dispatch PDF"** generates a formatted PDF dispatch with map preview, suspect details, and ranked ATM addresses for field officers.
5. **Killer Feature 2:** **"Human-in-the-Loop"** buttons (`Confirmed Interception` / `False Alarm`) to log operational feedback.
