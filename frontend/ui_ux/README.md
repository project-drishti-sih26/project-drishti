# 💻 Role 4: Frontend Engineer (UI/UX & Dashboard)

## 📌 Role Ownership & Mission
* **Role:** Frontend Engineer (Command Center UI, UX & Interactive Dashboards)
* **Goal:** Build the command center layout and user experience for law enforcement operators. Turn complex multi-hop financial cascades and machine learning predictions into rapid, high-contrast, actionable intelligence.
* **Tech Stack:** React.js, Tailwind CSS (Command Center Dark Theme), Lucide React, Recharts, Zustand, jspdf (Dispatch PDF generation).

---

## 📂 Folder Structure
```
frontend/ui_ux/
├── components/
│   ├── Header.jsx               # Top navigation bar, I4C branding, live incident ticker & UTC clock
│   ├── SidebarLeft.jsx          # Active case dossier & live transaction stream
│   ├── SidebarRight.jsx         # Top-5 predicted ATMs, survival time window, SHAP reasoning cards
│   ├── Alerts.jsx               # Urgent pulsing alert notification banner
│   ├── CaseFlow.jsx             # Visual victim -> mule -> cashout money trail graph
│   ├── PoliceDispatchModal.jsx  # Killer Feature 1: "1-Click Export to Police Dispatch PDF"
│   └── FeedbackActions.jsx      # Killer Feature 2: Human-in-the-loop operation feedback buttons
├── index.js                     # Clean component exports
└── README.md                    # Role 4 specification & guide
```

---

## 🎯 Key Deliverables
1. **3-Column Tactical Command Center:**
   - **Left Column:** Live Case Details & Transaction Flow (Victim -> Mule -> Hop accounts).
   - **Center Column:** Interactive Map Radar (imported from `gis/MapRadar.jsx`).
   - **Right Column:** Predicted Cashout ATMs ranked #1 to #5 with countdown timer & SHAP factors.
2. **Visual Money Trail Graph (`CaseFlow.jsx`):**
   - Renders animated nodes showing account numbers, timestamps, and amounts (`₹75,000`).
3. **Actionable Top-5 Prediction Cards (`SidebarRight.jsx`):**
   - Highlighting ATM location name, address, distance, estimated travel time.
   - Explainable AI (SHAP) badge: e.g. *"Proximity to past cashout (82%) + Active time pattern (18%)"*.
4. **Killer Feature 1: 1-Click Police Dispatch PDF (`PoliceDispatchModal.jsx`):**
   - Generates an official field dispatch sheet with suspect account, predicted ATM GPS, time window, and dispatch authorization stamp using `jspdf`.
5. **Killer Feature 2: Human-in-the-loop Feedback (`FeedbackActions.jsx`):**
   - One-touch operator buttons: `Confirmed Interception` and `False Alarm` to record ground truth and train the reinforcement loop.
