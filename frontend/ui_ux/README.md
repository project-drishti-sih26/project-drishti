# 💻 Role 4: Frontend Engineer (UI/UX & Dashboard)

## 📌 Role Ownership & Mission
* **Role:** Frontend Engineer (Modern SaaS Intelligence Dashboard)
* **Design Philosophy:** Soft, modern SaaS consumer-product aesthetic (inspired by Linear, Stripe Dashboard, Skymetrics). Prioritizes visual polish, approachable ergonomics, clean cards, and generous whitespace.
* **Aesthetic Highlights:**
  - **Color Palette:** Soft off-white / light grey background (`#f8fafc`), clean white card surfaces (`#ffffff`), and soft pastel accents (`indigo`, `rose`, `emerald`, `amber`).
  - **Card Geometry & Elevation:** Generous rounded corners (16–20px radius) with subtle, floating drop shadows (`shadow-[0_2px_8px_rgba(0,0,0,0.03)]`).
  - **Pill Badges:** Rounded chip badges for status, severity, and categories.
  - **Charts:** Two-tone gradient area line charts ("Cases Over Time") and clean donut charts ("Cases by Category").
  - **Action Ergonomics:** One solid dark rounded button (primary) and one outlined rounded button (secondary).

---

## 📂 Folder Structure
```
frontend/ui_ux/
├── components/
│   ├── CommandCenter.jsx        # Master SaaS layout with metric cards, 3 columns & charts
│   ├── Header.jsx               # Top navigation bar, Drishti branding, live status pill & profile
│   ├── Alerts.jsx               # Soft coral pastel alert banner with pill action button
│   ├── SidebarLeft.jsx          # Active case dossier & step-by-step money trail
│   ├── CaseFlow.jsx             # Soft step-by-step account cascade visual (Victim → Mule → ATM)
│   ├── CenterRadar.jsx          # Soft modern spatial radar & ATM interception map
│   ├── SidebarRight.jsx         # Large countdown timer, top-5 ranked ATM list & feedback actions
│   ├── FeedbackActions.jsx      # Modern primary dark + secondary outlined rounded buttons
│   └── PoliceDispatchModal.jsx  # Printable police dispatch order preview & jsPDF exporter
├── index.html                   # Standalone interactive live dashboard preview
├── index.js                     # Component exports
└── README.md                    # Role 4 specification & guide
```

---

## 🎯 Key Dashboard Deliverables
1. **Top Nav Bar (`Header.jsx`):**
   - Brand logo, navigation items, soft green live status pill badge ("Live Feed Online"), live clock, and profile avatar.
2. **Top Metric Cards Row (4 Cards):**
   - Active Cases (`24` `+12.4%`), Total Value at Risk (`₹42.8L` `+8.1%`), Cases Intercepted (`18` `+18.5%`), Avg Response Time (`12.4m` `-14.2% faster`).
3. **Main Case View & Step-by-Step Flow (`SidebarLeft.jsx` & `CaseFlow.jsx`):**
   - Selected case summary with siphoned amount, victim identity, and mule profile.
   - Soft step-by-step cascade flow: `Victim → Flagged Mule → Target ATM`.
4. **Spatial Radar Map (`CenterRadar.jsx`):**
   - Soft street network, uncertainty radius circle (1.8 km), patrol unit tracking (`PCR-12`), and colored ATM pins (1–5).
5. **Predictions Sidebar (`SidebarRight.jsx`):**
   - Large colorful countdown timer with urgency chip.
   - Top-5 ranked ATM list with pill badges, confidence %, travel time, and expandable AI reasoning.
   - Operator decision buttons (`Confirmed Interception` / `False Alarm`).
6. **Charts Section:**
   - Soft line chart ("Cases Over Time") with two-tone gradient fill.
   - Colorful donut chart ("Cases by Category") breaking down fraud vectors.
7. **Dispatch Export Sheet (`PoliceDispatchModal.jsx`):**
   - Official court-admissible dispatch sheet with 1-click PDF download via `jsPDF`.


