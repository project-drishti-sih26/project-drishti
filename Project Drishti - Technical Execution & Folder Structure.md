# **🛠️ Project Drishti: Master Technical Execution & Architecture Blueprint**

**SIH Problem Statement:** SIH26184 (Predictive Analytics for Cybercrime)

**Team Size:** 6 Members

**Architecture Style:** Microservices via GitHub Organization

## **1\. The Tech Stack & "Why We Chose It" (For the Judges)**

To win, you must justify your tech stack. Here is the exact stack and the argument for each:

### **Frontend (The Command Center)**

* **Framework:** **React.js (via Vite)** \- Vite is 10x faster than Create-React-App, crucial for hackathon speed.  
* **Styling:** **Tailwind CSS** \- For rapid UI prototyping and a native "Dark Mode" aesthetic.  
* **State Management:** **Zustand** \- Much lighter and faster to set up than Redux for handling live WebSocket payloads.  
* **Mapping:** **Mapbox GL JS** \- Vastly superior to Leaflet for rendering complex spatial data like H3 hex-grids and thousands of custom markers without lagging.  
* **Data Viz:** **Recharts** \- For transaction velocity graphs. Easy to integrate with React.

### **Backend (The Core Engine)**

* **Framework:** **FastAPI (Python)** \- Why not Django/Node.js? Because all our ML is in Python. FastAPI is async, natively supports WebSockets for real-time alerts, and is significantly faster than Flask.  
* **Database:** **PostgreSQL with PostGIS** \- PostGIS extension allows for advanced spatial queries (e.g., finding all ATMs within a 5km radius instantly).  
* **ORM:** **SQLAlchemy** \- For safe, injection-free database queries.

### **Machine Learning (The Predictive Brain)**

* **Spatial Indexing:** **H3 (Uber's Hexagonal Hierarchical Spatial Index)** \- Replaces standard latitude/longitude with hex grids, standardizing spatial data for the ML model.  
* **Ranking Algorithm:** **LightGBM (LambdaMART)** \- We are framing this as a "Learning-to-Rank" problem (like Google Search). LightGBM is the fastest and most accurate library for this.  
* **Time-to-Event Model:** **lifelines** \- For Survival Analysis (predicting *when* the withdrawal will happen).  
* **Explainability:** **SHAP (SHapley Additive exPlanations)** \- Translates ML weights into human-readable text.

### **Data Simulation & DevOps**

* **Simulation:** **Python Faker, pandas, networkx** \- For creating the massive synthetic transaction graphs.  
* **Deployment:** **Docker & Docker Compose** \- Containerizes the React app and FastAPI backend so they run flawlessly on the presentation laptop without environment errors.

## **2\. Granular Role Breakdown (Squad of 6\)**

### **⚙️ Role 1: Backend Engineer (APIs & Core Logic)**

* **Primary Duty:** Connect the DB, ML, and Frontend.  
* **Tasks:**  
  * Define SQLAlchemy models (Account, Transaction, PhysicalLocation, Case).  
  * Create POST /api/transactions to ingest simulated data.  
  * Write the trigger logic: *If incoming transfer \> ₹50,000 AND account\_type \== MULE \-\> Execute ML Script.*  
  * Establish ws://.../live\_alerts WebSocket to broadcast predictions.

### **🧠 Role 2: ML/AI Engineer (Predictive Engine)**

* **Primary Duty:** Build the WHERE and WHEN models.  
* **Tasks:**  
  * Code the **Fallback Heuristic**: Score \= (Fraud\_History × 0.7) \+ (1/Distance × 0.3).  
  * Train the LightGBM LambdaMART model to output a ranked Top-5 ATM list.  
  * Implement lifelines to output a time window (e.g., "14:30 \- 15:00").  
  * Wrap models in a Python function that Role 1 can call synchronously.

### **🗺️ Role 3: Frontend Engineer (Maps & GIS)**

* **Primary Duty:** Own the center-screen radar.  
* **Tasks:**  
  * Initialize Mapbox GL JS with a dark theme.  
  * Listen to Role 1's WebSocket.  
  * Write the map.flyTo() animation to zoom into the predicted coordinates.  
  * Overlay H3 Hex grids or radius circles over the danger zone.  
  * Render custom HTML markers for the Top-5 ATMs (Red for \#1, Orange for \#2-5).

### **💻 Role 4: Frontend Engineer (UI/UX & Dashboard)**

* **Primary Duty:** Own the sidebars, alerts, and user experience.  
* **Tasks:**  
  * Design the Tailwind CSS grid layout (Sidebar Left, Map Center, Sidebar Right).  
  * Build the "Live Case Flow" showing money moving from Victim \-\> Mule.  
  * Design the Top-5 Ranking List panel with hover states.  
  * **Killer Feature:** Build the "Export to PDF" button for police dispatch.  
  * **Killer Feature:** Add "Confirmed" / "False Alarm" buttons for Human-in-the-Loop feedback.

### **📊 Role 5: Data Engineer (Synthetic World Builder)**

* **Primary Duty:** Provide the fuel (data) for the system.  
* **Tasks:**  
  * Generate atms\_master.csv containing \~200 fake ATMs with real GPS coordinates in your demo city.  
  * Pre-compute the Distance Matrix (Time taken to travel from H3 hexes to these ATMs) to save hackathon compute time.  
  * Generate historical\_transactions.csv (10,000 rows) linking mules to ATMs.  
  * Write run\_live\_demo.py — the script you run during the presentation to push a live fraud transaction into Role 1's API.

### **🚀 Role 6: Integrator & Pitch Strategist (DevOps/QA)**

* **Primary Duty:** System stability and presentation.  
* **Tasks:**  
  * Write docker-compose.yml to spin up PostgreSQL, FastAPI, and React in one command.  
  * Resolve all CORS (Cross-Origin Resource Sharing) errors between React and FastAPI.  
  * Test End-to-End Latency: The time between Role 5 pressing ENTER and Role 3's map moving must be \< 2 seconds.  
  * Design the PowerPoint pitch deck and script the live demo.

## **3\. Standardized Folder Structures (GitHub Org)**

Create a GitHub Organization (e.g., project-drishti-sih26). Create the following 4 repositories and enforce this exact folder structure to avoid chaos.

### **Repo 1: frontend-dashboard (React/Vite)**

*(Owned by Roles 3 & 4\)*

frontend-dashboard/  
├── public/                   
├── src/  
│   ├── assets/             \# Map marker SVGs, logos  
│   ├── components/           
│   │   ├── Map/              
│   │   │   ├── MapRadar.jsx     \# Mapbox initialization  
│   │   │   └── Markers.jsx      \# Custom HTML markers  
│   │   ├── UI/              
│   │   │   ├── SidebarLeft.jsx  \# Case details  
│   │   │   ├── SidebarRight.jsx \# Top 5 list & Time window  
│   │   │   └── Alerts.jsx       \# Flashing red banners  
│   ├── store/              \# Zustand state (useAlertStore.js)  
│   ├── services/           \# WebSocketClient.js, api.js  
│   ├── utils/              \# PDF generator function, time formatters  
│   ├── App.jsx             \# Main layout grid  
│   └── main.jsx  
├── .env                    \# VITE\_MAPBOX\_TOKEN, VITE\_WS\_URL  
├── tailwind.config.cjs  
├── package.json  
└── Dockerfile              \# Nginx multi-stage build  
