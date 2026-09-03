# 👁️ Project Drishti: Master Blueprint & Technical Specification

> **Smart India Hackathon (SIH 2026)**  
> **Problem Statement ID:** SIH26184 (Predictive Analytics for Cybercrime)  
> **Target Agency:** Indian Cybercrime Coordination Centre (I4C), Ministry of Home Affairs  
> **Domain:** Machine Learning, Spatial-Temporal Forecasting, Fintech Security  
> **Team Size:** 6 Members | **Architecture:** Microservices / Monorepo  

---

## 📑 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [The Tech Stack & "Why We Chose It" (Defense for Judges)](#2-the-tech-stack--why-we-chose-it-defense-for-judges)
3. [Granular Role Breakdown (Squad of 6)](#3-granular-role-breakdown-squad-of-6)
4. [The Machine Learning Engine (WHERE & WHEN)](#4-the-machine-learning-engine-where--when)
5. [Complete Database Schema (SQLAlchemy Reference)](#5-complete-database-schema-sqlalchemy-reference)
6. [Standardized Folder Structure](#6-standardized-folder-structure)
7. [Live Demonstration Script & Presentation Pitch](#7-live-demonstration-script--presentation-pitch)

---

## 1. Executive Summary

### The Problem (Reactive Policing)
Currently, law enforcement relies on **reactive tracing** for cybercrimes. When a victim reports a cyber fraud (e.g., OTP scam, investment scam, phishing), scammers rapidly route the funds through a multi-layered cascade of **"mule" bank accounts** and withdraw the cash from distant physical ATMs or Banking Correspondents (BCs). Police are only alerted *after* the cash has disappeared, resulting in zero account balance and lost trails.

### The Solution (Proactive Forecasting)
**Project Drishti** is a proactive AI intelligence radar. It monitors live transaction graphs and, the moment stolen funds hit a known mule network, predicts the scammers' next move *before* it happens.

It answers two exact operational questions during an active fraud event:
1. **WHERE:** Predicts and ranks the **Top-5 specific physical ATMs/locations** the mule will use.
2. **WHEN:** Forecasts the **exact time window** (e.g., *"in 25–45 minutes"*) the cash withdrawal will occur.

> ⏱️ **Operational Outcome:** Gives police and field patrol units a **20-minute actionable window** to physically intercept the criminal at the cashout point.

---

## 2. The Tech Stack & "Why We Chose It" (Defense for Judges)

To win in SIH, every technical choice must be justified with operational advantages:

### Frontend (The Command Center)
* **Framework — React.js (via Vite):** Vite is 10x faster than Create-React-App, crucial for fast UI prototyping and instant WebSocket hot updates during live demos.
* **Styling — Tailwind CSS:** Enables rapid UI prototyping with a sleek, native dark-mode command center aesthetic.
* **State Management — Zustand:** Far lighter and faster to set up than Redux for handling high-frequency live WebSocket alert payloads.
* **Mapping — Mapbox GL JS:** Hardware-accelerated WebGL rendering is vastly superior to Leaflet for rendering dynamic H3 spatial hex-grids, danger radiuses, and custom animated markers without UI lag.
* **Data Visualization — Recharts:** Lightweight transaction velocity and flow charts seamlessly integrated into React.

### Backend (The Core Engine)
* **Framework — FastAPI (Python):** Native async architecture, built-in WebSocket support for real-time alerting, and zero IPC overhead when calling Python ML models (unlike Django or Node.js).
* **Database — PostgreSQL with PostGIS:** PostGIS spatial extension enables high-performance geographical queries (e.g., finding all candidate ATMs within a 5 km bounding box in milliseconds).
* **ORM — SQLAlchemy 2.0:** Safe, type-annotated, injection-free database transactions and migrations.

### Machine Learning (The Predictive Brain)
* **Spatial Indexing — Uber H3:** Replaces arbitrary lat/long coordinates with regular hexagonal spatial hierarchies, standardizing spatial candidate inputs.
* **Candidate Ranking — LightGBM (LambdaMART):** Formulates ATM prediction as a Learning-to-Rank (LTR) problem (similar to search engine rankings), outperforming flawed binary classification models.
* **Time-to-Event Model — `lifelines`:** Survival Analysis (Kaplan-Meier / Cox Proportional Hazards) models right-censored fraud duration to output accurate time windows rather than rigid point estimates.
* **AI Explainability — SHAP (SHapley Additive exPlanations):** Eliminates black-box distrust by converting model weights into natural language operational reasons for law enforcement.

### Data Simulation & DevOps
* **Synthetic Graph Simulation — Python Faker, pandas, networkx:** Generates realistic 10,000+ transaction multi-hop mule account topologies with genuine GPS coordinates.
* **Containerization — Docker & Docker Compose:** Containerizes PostgreSQL/PostGIS, FastAPI backend, and React frontend for one-command startup on any presentation laptop with zero environment mismatch.

---

## 3. Granular Role Breakdown (Squad of 6)

| Role | Title | Core Focus | Module Directory | Key Deliverables |
|:---:|:---|:---|:---|:---|
| **Role 1** | **Backend Engineer** | APIs & Core Logic | `backend/` | SQLAlchemy models, FastAPI REST endpoints, ML trigger condition (`> ₹50,000` + Mule), WebSocket broadcast (`/live_alerts`). |
| **Role 2** | **ML/AI Engineer** | Predictive Brain | `ml_engine/` | LightGBM LambdaMART ranker, `lifelines` survival time model, SHAP explainability strings, cold-start fallback formula. |
| **Role 3** | **Frontend Engineer (GIS)** | Maps & Radar | `frontend/gis/` | Mapbox GL JS dark radar, smooth `map.flyTo()` zoom animations, H3 danger hex overlays, custom pulsing markers. |
| **Role 4** | **Frontend Engineer (UI/UX)** | Dashboard & UX | `frontend/ui_ux/` | 3-column layout, Live Case Flow visualizer, Top-5 ranking cards, 1-Click Police Dispatch PDF export, human feedback buttons. |
| **Role 5** | **Data Engineer** | World Simulation | `simulation/` | `atms_master.csv`, pre-computed travel distance matrix, 10,000 synthetic mule transactions, presentation trigger `run_live_demo.py`. |
| **Role 6** | **Integrator & DevOps** | Stability & Pitch | Root, `docker/`, `docs/` | `docker-compose.yml`, CORS configuration, E2E latency optimization (< 2s), presentation deck and live demo choreography. |

---

## 4. The Machine Learning Engine (WHERE & WHEN)

The prediction pipeline replaces traditional classification with a **4-step Retrieval + Learning-to-Rank (LTR) + Survival Analysis** pipeline:

```
  [ Live Transaction ]
          │
          ▼
┌───────────────────┐
│ Activation Trigger│  Incoming Amount > ₹50,000 AND Account == MULE
└─────────┬─────────┘
          │
          ├─────────────────────────────────────────┐
          ▼                                         ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│        WHEN ENGINE        │         │       WHERE ENGINE        │
│   Survival Analysis       │         │  Phase 1: Candidate Filter│
│  (lifelines / Cox PH)     │         │  H3 Hex + Distance Matrix │
│  Forecasts Cashout Window │         │  100k ATMs -> ~200 Reachable
└─────────┬─────────────────┘         └─────────────┬─────────────┘
          │                                         ▼
          │                           ┌───────────────────────────┐
          │                           │ Phase 2: LambdaMART Rank  │
          │                           │ LightGBM scores Top-5 ATMs│
          │                           └─────────────┬─────────────┘
          │                                         ▼
          │                           ┌───────────────────────────┐
          │                           │   Phase 3: SHAP Explain   │
          │                           │  Human-readable dispatch  │
          │                           └─────────────┬─────────────┘
          │                                         │
          └────────────────────┬────────────────────┘
                               ▼
              ┌─────────────────────────────────┐
              │ Live Prediction Payload (ws://) │
              │ - Top-5 Ranked Physical ATMs    │
              │ - 25–45 min Interception Window │
              │ - Dispatch Explanation Strings  │
              └─────────────────────────────────┘
```

### Step 1: Activation Trigger
The model remains idle until a rapid transfer lands in a flagged mule account:
$$\text{Incoming\_Amount} > \text{₹50,000} \quad \land \quad \text{Account\_Type} == \text{"Mule"}$$

### Step 2: WHEN Engine (Time Forecasting)
* **Model:** Survival Analysis (`lifelines` — Kaplan-Meier / Cox Proportional Hazards).
* **Output:** Probability distribution of withdrawal time window:
  $$\text{Window: } [T_{\text{start}}, T_{\text{end}}] \quad \text{e.g., "14:30 – 15:00 (in 28 to 43 minutes)"}$$

### Step 3: WHERE Engine (Two-Stage Spatial Prediction)
* **Phase 1 (Candidate Retrieval):** Uses H3 spatial indexing and a **Pre-computed Distance Matrix** to prune 100,000 national ATMs down to ~200 candidates reachable by road within the predicted time window.
* **Phase 2 (Learning-to-Rank):** LightGBM (LambdaMART) ranks candidate ATMs using:
  1. `distance_to_last_known_node` (road travel time)
  2. `atm_historical_fraud_count` (fraud density)
  3. `mule_atm_affinity` (historical pattern of this mule network)
* **Cold-Start Fallback Heuristic:** If a mule account is 100% new with no prior graph history, the system dynamically activates the fallback formula:
  $$\text{Score} = (\text{Fraud\_History} \times 0.7) + \left(\frac{1}{\text{Distance}} \times 0.3\right)$$

### Step 4: AI Explainability (SHAP)
SHAP values translate mathematical weights into plain-language justification for police:
> *"Rank #1: 6-minute road travel time + historically used by this mule network in 3 past frauds."*

---

## 5. Complete Database Schema (SQLAlchemy Reference)

Directly consolidated from `Db Design demo.py`:

```python
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enums for strict data validation
class AccountType(enum.Enum):
    STANDARD = "Standard"
    MULE = "Mule"

class LocationType(enum.Enum):
    ATM = "ATM"
    BRANCH = "Branch"
    BC = "Banking_Correspondent"

# 1. Accounts Table
class Account(Base):
    __tablename__ = 'accounts'
    
    account_id = Column(String, primary_key=True, index=True)
    account_type = Column(Enum(AccountType), default=AccountType.STANDARD)
    risk_score = Column(Float, default=0.0)  # ML updates this dynamically

# 2. Transactions Table (The Graph Edges)
class Transaction(Base):
    __tablename__ = 'transactions'
    
    tx_id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey('accounts.account_id'))
    receiver_id = Column(String, ForeignKey('accounts.account_id'))
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Track if this specific transaction was flagged in a case
    case_id = Column(String, ForeignKey('cases.case_id'), nullable=True)

# 3. Physical Locations Table (ATMs & Banking Correspondents)
class PhysicalLocation(Base):
    __tablename__ = 'physical_locations'
    
    location_id = Column(String, primary_key=True, index=True)
    location_type = Column(Enum(LocationType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    historical_fraud_count = Column(Integer, default=0)  # Crucial for fallback heuristic

# 4. Cybercrime Cases Table
class Case(Base):
    __tablename__ = 'cases'
    
    case_id = Column(String, primary_key=True, index=True)  # e.g., CYB-2026-00123
    victim_account_id = Column(String, ForeignKey('accounts.account_id'))
    compromised_amount = Column(Float, nullable=False)
    status = Column(String, default="ACTIVE")
```

---

## 6. Standardized Folder Structure

```
project-drishti/
├── .gitignore                         # Comprehensive ignore patterns
├── .env.example                       # Unified environment template
├── docker-compose.yml                 # Role 6: Full-stack container orchestration
├── README.md                          # Master pitch & setup guide
├── PROJECT_BLUEPRINT.md               # THIS MASTER SPECIFICATION FILE
│
├── backend/                           # ⚙️ [Role 1: Backend Engineer]
│   ├── app/
│   │   ├── api/endpoints/             # REST & WebSocket route controllers
│   │   ├── core/                      # Config, security, JWT
│   │   ├── db/                        # Session & connection management
│   │   ├── models/                    # SQLAlchemy models (Account, Case, Location, Tx)
│   │   ├── schemas/                   # Pydantic validation models
│   │   └── services/                  # Trigger service & business logic
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── ml_engine/                         # 🧠 [Role 2: ML/AI Engineer]
│   ├── models/                        # LambdaMART ranker, lifelines survival, fallback
│   ├── pipelines/                     # H3 spatial filter, SHAP explainability, inference
│   ├── weights/                       # Pretrained model weights
│   ├── notebooks/                     # Training & EDA notebooks
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                          # 🗺️💻 [Roles 3 & 4: Frontend Engineers]
│   ├── gis/                           # 🗺️ [Role 3: Maps & GIS Radar]
│   │   ├── components/                # MapRadar.jsx, Markers.jsx, H3HexLayer.jsx
│   │   ├── index.js
│   │   └── README.md
│   ├── ui_ux/                         # 💻 [Role 4: UI/UX & Dashboard]
│   │   ├── components/                # Header, SidebarLeft, SidebarRight, Alerts, CaseFlow, DispatchModal
│   │   ├── index.js
│   │   └── README.md
│   ├── public/
│   ├── src/
│   │   ├── assets/                    # Map icons, badges, markers
│   │   ├── services/                  # WebSocketClient.js & api.js
│   │   ├── store/                     # useAlertStore.js (Zustand)
│   │   ├── utils/                     # PDF dispatch generator & formatters
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
│
├── simulation/                        # 📊 [Role 5: Data Engineer]
│   ├── data/                          # atms_master.csv, distance_matrix, historical_tx.csv
│   ├── generators/                    # Faker & NetworkX generators
│   ├── run_live_demo.py               # Judge demo trigger script
│   ├── requirements.txt
│   └── README.md
│
├── docker/                            # 🚀 [Role 6: Integrator & DevOps]
│   └── README.md                      # Production deployment guides
│
└── docs/                              # 🎬 [Role 6: Pitch & Demo Strategy]
    └── README.md                      # Live demo script & presentation checklist
```

---

## 7. Live Demonstration Script & Presentation Pitch

### The 3-Minute Winning Sequence:
1. **The Problem (0:00 – 0:45):**  
   Present the reality of cyber fraud: *"Current policing only reacts after cash has been withdrawn. By the time accounts freeze, the money is gone."*
2. **The Live Trigger (0:45 – 1:30):**  
   Role 5 executes `python simulation/run_live_demo.py`. Within < 1 second:
   - Frontend radar flashes Red Alert: **"ACTIVE MULE CASHOUT IN PROGRESS"**.
   - Mapbox camera smoothly executes `map.flyTo()` zoom to the suspect zone.
   - H3 spatial hex overlay illuminates the candidate search perimeter.
   - Top-5 ATM markers appear (Pulsing Red for #1, Orange for #2–5).
3. **The Intelligence (1:30 – 2:15):**  
   Showcase the two answers:
   - **WHEN:** Survival Analysis cashout window: *"Withdrawal expected between 14:32 and 14:48"*.
   - **WHERE:** Top-5 ranked ATMs with SHAP explainability cards.
4. **The Actionable Impact (2:15 – 3:00):**  
   Click **"Export to Police Dispatch PDF"** to generate an operational field dispatch ready for instant radio/WhatsApp dispatch to local PCR vans.

---

<div align="center">
  <b>Project Drishti — Smart India Hackathon (SIH 2026)</b><br />
  <i>Indian Cybercrime Coordination Centre (I4C), Ministry of Home Affairs</i>
</div>
