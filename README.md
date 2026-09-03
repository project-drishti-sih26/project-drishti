<div align="center">

# 👁️ PROJECT DRISHTI
### Proactive Predictive Intelligence Radar for Cybercrime & Mule Account Interception

[![SIH 2026](https://img.shields.io/badge/SIH-2026-orange.svg?style=for-the-badge)](https://www.sih.gov.in/)
[![Problem Statement](https://img.shields.io/badge/PS_ID-SIH26184-blue.svg?style=for-the-badge)](https://www.sih.gov.in/)
[![Organization](https://img.shields.io/badge/Agency-I4C_%7C_MHA-red.svg?style=for-the-badge)](https://i4c.mha.gov.in/)
[![GitHub Org](https://img.shields.io/badge/GitHub-project--drishti--sih26-black.svg?style=for-the-badge&logo=github)](https://github.com/project-drishti-sih26)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Transforming Cybercrime Policing from Reactive Tracing to Proactive Physical Interception</b>
  <br />
  <i>Predicting WHERE and WHEN fraudsters will withdraw cash before they reach the ATM.</i>
</p>

</div>

---

## 📑 Table of Contents
- [1. Executive Summary & Problem Context](#-1-executive-summary--problem-context)
- [2. The Drishti Solution](#-2-the-drishti-solution)
- [3. Dual-Engine Machine Learning Pipeline](#-3-dual-engine-machine-learning-pipeline)
- [4. Granular Team Role Breakdown (Squad of 6)](#-4-granular-team-role-breakdown-squad-of-6)
- [5. Master Folder Structure](#-5-master-folder-structure)
- [6. Master System Architecture](#-6-master-system-architecture)
- [7. Tech Stack & Judge Justification](#-7-tech-stack--judge-justification)
- [8. Team Git Workflow & Quickstart](#-8-team-git-workflow--quickstart)
- [9. SIH Presentation & Live Demo Flow](#-9-sih-presentation--live-demo-flow)

---

## 🚨 1. Executive Summary & Problem Context

* **SIH Problem Statement:** **SIH26184**  
* **Ministry / Partner Agency:** Indian Cybercrime Coordination Centre (I4C), Ministry of Home Affairs  
* **Domain:** Machine Learning, Spatial-Temporal Forecasting, Graph Intelligence, Fintech Security  

### The Problem: Reactive Policing
When an innocent citizen falls victim to a cyber financial fraud (e.g., OTP scam, KYC phishing, investment scam), scammers rapidly siphon the stolen money through an automated, multi-tiered hierarchy of **"mule" bank accounts**. Within minutes, runners physically withdraw hard currency from distant ATMs or Banking Correspondents (BCs). 

Currently, law enforcement relies entirely on **reactive tracing**. Police begin investigations hours or days after the incident report. By the time accounts are frozen via 1930 / CFCFRMS, the accounts have zero balance and the criminal has disappeared into thin air.

---

## ⚡ 2. The Drishti Solution

**Project Drishti** is an active intelligence radar for cyber enforcement agencies. It ingests live transaction streams and, the exact microsecond stolen funds land into a flagged mule account, proactively answers two critical questions:

```
                  ┌────────────────────────────────────────┐
                  │          ACTIVE FRAUD EVENT            │
                  └───────────────────┬────────────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
  ┌─────────────────────────┐                   ┌─────────────────────────┐
  │         WHERE?          │                   │          WHEN?          │
  │  Ranked Top-5 Physical  │                   │  Exact cashout window   │
  │  ATMs the mule is heading│                   │  (e.g., "in 25–40 min") │
  │  to right now.          │                   │  derived from survival. │
  └─────────────────────────┘                   └─────────────────────────┘
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 🚨 ACTIONABLE POLICE DISPATCH (20 MIN) │
                  │  Patrol units alerted with exact route │
                  │  and high-probability ATM coordinates. │
                  └────────────────────────────────────────┘
```

---

## 🧠 3. Dual-Engine Machine Learning Pipeline

Instead of naive binary classification, Drishti formulates interception as a **Learning-to-Rank (LTR)** and **Survival Analysis** problem:

### Step 1: Activation Trigger
The ML pipeline activates when:
$$\text{Incoming Transaction} > \text{₹50,000} \quad \text{AND} \quad \text{Account Type} == \text{MULE}$$

### Step 2: WHEN Engine (Survival Time Forecasting)
* **Algorithm:** Survival Analysis (`lifelines` — Kaplan-Meier / Cox Proportional Hazards).
* **Target:** Forecasts the cumulative hazard function to provide the probability density of withdrawal time:
  $$\text{Output: Active Cashout Window } [T_{\text{start}}, T_{\text{end}}] \quad (\text{e.g., } 14:30 - 15:00)$$

### Step 3: WHERE Engine (Two-Stage Spatial Retrieval + Ranking)
1. **Candidate Retrieval (Uber H3 Spatial Indexing):**  
   Filters 100,000+ national ATMs down to ~200 reachable candidates within the predicted travel window using precomputed road travel distance matrices.
2. **Learning-to-Rank (LightGBM LambdaMART):**  
   Scores and ranks candidate ATMs based on:
   - Road travel duration from last known mule coordinate
   - ATM historical fraud density (`historical_fraud_count`)
   - Mule network spatial affinity & clustering
3. **Cold-Start Fallback Heuristic:**  
   If a mule account is brand new with zero history, the system dynamically switches to the heuristic fallback formula:
   $$\text{Score} = (\text{Historical\_Fraud\_Density} \times 0.7) + \left(\frac{1}{\text{Road\_Distance}} \times 0.3\right)$$

### Step 4: AI Explainability (SHAP)
Transforms complex tree weights into actionable, human-readable intelligence for field officers:
> *"Rank #1 ATM: 6-minute road travel time + historically utilized in 4 prior mule cashouts."*

---

## 👥 4. Granular Team Role Breakdown (Squad of 6)

To maximize development velocity during the hackathon, each member has strict code ownership over their designated module:

| Role | Title | Core Focus | Module Directory | Primary Stack | Key Deliverable |
|:---:|:---|:---|:---|:---|:---|
| **Role 1** | **Backend Engineer** | APIs & Core Logic | [`backend/`](backend/) | FastAPI, SQLAlchemy, PostgreSQL/PostGIS, WebSockets | Ingestion REST endpoints, trigger logic, and WebSocket alerts. |
| **Role 2** | **ML/AI Engineer** | Predictive Engine | [`ml_engine/`](ml_engine/) | LightGBM, `lifelines`, SHAP, H3-py, osmnx | Top-5 LambdaMART ranker, survival time window, explainability strings. |
| **Role 3** | **Frontend Engineer** | Maps & GIS Radar | [`frontend/src/components/Map/`](frontend/src/components/Map/) | React, Mapbox GL JS, H3 Spatial | Dynamic radar map, `map.flyTo()` zoom animations, H3 danger hexes. |
| **Role 4** | **Frontend Engineer** | UI/UX & Dashboard | [`frontend/src/components/UI/`](frontend/src/components/UI/) | React, Tailwind CSS, Zustand, Recharts | Dark command layout, money flow visualizer, 1-Click Police PDF. |
| **Role 5** | **Data Engineer** | Synthetic World Builder | [`simulation/`](simulation/) | Faker, pandas, networkx | `atms_master.csv`, distance matrix, and presentation `run_live_demo.py`. |
| **Role 6** | **Integrator & Pitch** | DevOps / QA / Strategy | Root, [`docker/`](docker/), [`docs/`](docs/) | Docker Compose, Nginx, Slide Deck | Unified startup, latency guarantees (< 2s), pitch script & deck. |

---

## 📂 5. Master Folder Structure

```
project-drishti/
├── .gitignore                         # Python, Node, PostGIS, IDE ignores
├── .env.example                       # Shared environment configuration template
├── docker-compose.yml                 # Role 6: Single-command orchestration
├── README.md                          # Master project documentation & guide
│
├── backend/                           # ⚙️ [ROLE 1: Backend Engineer]
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/             # REST & WebSocket route handlers
│   │   ├── core/                      # Configuration, settings & auth
│   │   ├── db/                        # Database connection & session factory
│   │   ├── models/                    # SQLAlchemy ORM models (Account, Case, Location, Tx)
│   │   ├── schemas/                   # Pydantic validation schemas
│   │   └── services/                  # Ingestion & ML trigger logic
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── ml_engine/                         # 🧠 [ROLE 2: ML/AI Engineer]
│   ├── models/                        # LambdaMART ranker, lifelines survival, fallback
│   ├── pipelines/                     # H3 spatial filter, SHAP explainability, inference
│   ├── weights/                       # Serialized model checkpoints
│   ├── notebooks/                     # Training & EDA notebooks
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                          # 🗺️💻 [ROLES 3 & 4: Frontend Engineers]
│   ├── public/                        # Static assets & icons
│   ├── src/
│   │   ├── assets/                    # Custom map marker SVGs & police badges
│   │   ├── components/
│   │   │   ├── Map/                   # 🗺️ Role 3: MapRadar.jsx, Markers.jsx, H3HexLayer.jsx
│   │   │   └── UI/                    # 💻 Role 4: SidebarLeft.jsx, SidebarRight.jsx, Alerts.jsx
│   │   ├── services/                  # WebSocket listener & REST clients
│   │   ├── store/                     # Zustand store (useAlertStore.js)
│   │   ├── utils/                     # 1-Click Police PDF generator & date formatters
│   │   ├── App.jsx
│   │   ├── index.css                  # Tailwind dark theme & radar animations
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
│
├── simulation/                        # 📊 [ROLE 5: Data Engineer]
│   ├── data/                          # atms_master.csv, distance_matrix, historical_tx.csv
│   ├── generators/                    # Faker & NetworkX graph data generators
│   ├── run_live_demo.py               # Presentation trigger script
│   ├── requirements.txt
│   └── README.md
│
├── docker/                            # 🚀 [ROLE 6: Integrator & DevOps]
│   └── README.md                      # Deployment instructions & production configs
│
└── docs/                              # 🎬 [ROLE 6: Pitch & Documentation]
    └── README.md                      # 3-minute pitch script, slide deck guide & demo walkthrough
```

---

## 🏛️ 6. Master System Architecture

```
                                [ Data Stream / Simulation ]
                                             │
                                             │ POST /api/v1/transactions
                                             ▼
                             ┌───────────────────────────────┐
                             │       FastAPI Ingestion       │
                             └───────────────┬───────────────┘
                                             │ (Trigger Condition Met)
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               ML PREDICTIVE ENGINE                                     │
│                                                                                        │
│   ┌───────────────────────────────────┐    ┌───────────────────────────────────────┐   │
│   │           WHEN ENGINE             │    │             WHERE ENGINE              │   │
│   │  Survival Analysis (lifelines)    │    │  Spatial H3 Hex Candidate Pruning     │   │
│   │  Predicts Cashout Time Window     │    │  (100k ATMs -> ~200 reachable ATMs)   │   │
│   └─────────────────┬─────────────────┘    └───────────────────┬───────────────────┘   │
│                     │                                          │                       │
│                     │                      ┌───────────────────▼───────────────────┐   │
│                     │                      │       LightGBM LambdaMART LTR         │   │
│                     │                      │       Rank Top-5 Candidate ATMs       │   │
│                     │                      └───────────────────┬───────────────────┘   │
│                     │                                          │                       │
│                     │                      ┌───────────────────▼───────────────────┐   │
│                     │                      │          SHAP Explainability          │   │
│                     │                      │    Human-readable dispatch text       │   │
│                     │                      └───────────────────┬───────────────────┘   │
│                     │                                          │                       │
│                     └──────────────────────┬───────────────────┘                       │
└────────────────────────────────────────────┼───────────────────────────────────────────┘
                                             │ WebSocket Broadcast (ws://.../live_alerts)
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND COMMAND CENTER RADAR                                │
│                                                                                        │
│  ┌───────────────────────┐  ┌───────────────────────────────┐  ┌────────────────────┐  │
│  │   CASE FLOW (Left)    │  │       MAPBOX RADAR (Center)   │  │   TOP-5 ATMS (Right│  │
│  │ - Victim Info         │  │ - Dark Theme Spatial Radar    │  │ - Ranked Cards     │  │
│  │ - Mule Account Node   │  │ - Animated flyTo() camera     │  │ - Travel Duration  │  │
│  │ - Amount & Fraud Type │  │ - H3 Danger Zone Hex Overlays │  │ - SHAP Reasonings  │  │
│  │ - Money Trail Graph   │  │ - Pulsing Red/Amber Markers   │  │ - Dispatch PDF btn │  │
│  └───────────────────────┘  └───────────────────────────────┘  └────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 7. Tech Stack & Judge Justification

| Layer | Technology | Why We Chose It (The Defense for Judges) |
|---|---|---|
| **Frontend Framework** | **React.js + Vite** | Vite delivers sub-second HMR and 10x faster startup than CRA. Essential for real-time state responsiveness. |
| **Mapping Engine** | **Mapbox GL JS** | Hardware-accelerated WebGL rendering supports dense H3 hexagonal meshes and custom CSS markers without frame drops. |
| **State Management** | **Zustand** | Zero-boilerplate, ultra-lightweight state manager ideal for high-frequency WebSocket alert ingestion. |
| **Backend Framework** | **FastAPI (Python)** | Asynchronous event loop with native WebSocket support. Executes Python ML pipelines without IPC overhead. |
| **Database & Spatial**| **PostgreSQL + PostGIS**| Industry-standard relational data integrity paired with PostGIS indexing for ultra-fast spatial bounding box queries. |
| **ML Ranking** | **LightGBM (LambdaMART)** | Learning-to-Rank (LTR) frames ATM prediction as search ranking, vastly outperforming flawed binary classification. |
| **ML Survival Time** | **`lifelines` (Survival Analysis)** | Models time-to-event dynamics with right-censored fraud data, producing probability windows rather than point estimates. |
| **ML Explainability** | **SHAP** | Eliminates the "black-box" barrier, delivering interpretable reasons necessary for law enforcement confidence. |
| **Data Simulation** | **Faker + NetworkX** | Generates topologically authentic multi-hop mule networks with real GPS coordinates. |
| **DevOps** | **Docker & Docker Compose** | Guarantees identical execution environments on presentation hardware with zero environment mismatch. |

---

## 🛠️ 8. Team Git Workflow & Quickstart

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js 18+](https://nodejs.org/) & [Python 3.11+](https://www.python.org/)
- Git configured with SSH key

### 1. Clone the Repository
```bash
git clone git@github.com:project-drishti-sih26/project-drishti.git
cd project-drishti
```

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Spin Up the Complete Stack via Docker
```bash
docker-compose up --build
```
* **Frontend Radar:** `http://localhost:5173`
* **FastAPI Docs:** `http://localhost:8000/docs`
* **PostgreSQL:** `localhost:5432`

### 4. Running the Live Simulation Demo
In a separate terminal:
```bash
python simulation/run_live_demo.py
```

### 5. Git Branching Rules for the 6 Members
Each member works in their designated branch to prevent merge conflicts:
* Role 1 (Backend): `feat/backend-core`
* Role 2 (ML/AI): `feat/ml-pipeline`
* Role 3 (Frontend Maps): `feat/frontend-radar`
* Role 4 (Frontend UI): `feat/frontend-dashboard`
* Role 5 (Data Simulation): `feat/data-simulation`
* Role 6 (DevOps / Integration): `feat/devops-docker`

---

## 🏆 9. SIH Presentation & Live Demo Flow

```
   Step 1: Open Frontend Command Center on big screen (Mapbox Radar active).
   Step 2: Role 5 presses ENTER on `simulation/run_live_demo.py`.
   Step 3: < 1 second later:
           - Screen flashes red alert: "CRITICAL FRAUD EVENT DETECTED".
           - Radar map automatically executes smooth `flyTo()` zoom to suspect zone.
           - H3 spatial hex overlay highlights high-risk boundary.
           - Top-5 ranked ATM markers pop up (Red for #1, Orange for #2-5).
   Step 4: Show Survival Analysis cashout window: "Cashout expected in 27–41 mins".
   Step 5: Show SHAP Explainability: "Rank #1 chosen due to travel time + prior mule usage".
   Step 6: Click "Export to Police Dispatch PDF" -> Instant PDF for field officer dispatch.
```

---

<div align="center">
  <b>Built with ❤️ by Team Project Drishti for Smart India Hackathon (SIH 2026)</b>
</div>
