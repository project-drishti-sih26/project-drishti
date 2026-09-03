# 👁️ Project Drishti: Predictive Analytics for Cybercrime

> **Smart India Hackathon (SIH 2026)**  
> **Problem Statement ID:** SIH26184  
> **Ministry / Organization:** Indian Cybercrime Coordination Centre (I4C), Ministry of Home Affairs  
> **GitHub Organization:** [project-drishti-sih26](https://github.com/project-drishti-sih26)  
> **Domain:** Machine Learning, Spatial-Temporal Forecasting, Fintech Security  

---

## 📌 1. Executive Summary

### The Problem (Reactive Policing)
Currently, law enforcement relies on reactive tracing for cyber frauds (OTP scams, phishing, investment frauds). When funds are reported stolen, scammers route money rapidly across multiple layers of "mule" bank accounts and withdraw cash at distant ATMs or Banking Correspondents (BCs). By the time police receive the complaint and freeze accounts, the cash is already gone.

### The Solution (Proactive Forecasting)
**Project Drishti** is a proactive AI intelligence radar. It monitors live transaction graphs and, the moment stolen funds hit a known mule network, predicts the scammers' next move *before* it happens.

It answers two exact operational questions:
1. **WHERE:** Predicts the **Top-5 specific physical ATMs/locations** the mule will use (Ranked).
2. **WHEN:** Forecasts the **exact time window** (e.g., *"in 25–45 minutes"*) the cash withdrawal will occur.

> ⏱️ **Operational Outcome:** Gives field officers and local police a 20+ minute actionable window to intercept criminals at physical cashout points.

---

## 🏗️ 2. System Architecture & Tech Stack

```
   [ Victim Transaction ]
            │
            ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                FastAPI Ingestion & WebSockets               │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ (Trigger: Mule Account Hit)
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                    ML Predictive Engine                     │
   │  ┌─────────────────────────┐   ┌──────────────────────────┐ │
   │  │   WHEN: lifelines       │   │  WHERE: Spatial Filter   │ │
   │  │   Survival Analysis     │   │  (H3 Hex + Distance Mat) │ │
   │  └─────────────────────────┘   └────────────┬─────────────┘ │
   │                                             ▼               │
   │                                ┌──────────────────────────┐ │
   │                                │  LightGBM (LambdaMART)   │ │
   │                                │  Top-5 Candidate Ranking │ │
   │                                └────────────┬─────────────┘ │
   │                                             ▼               │
   │                                ┌──────────────────────────┐ │
   │                                │   SHAP Explainability    │ │
   │                                └──────────────────────────┘ │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ Live Prediction Stream (WS)
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │           Frontend Command Center (React + Mapbox)          │
   │  - Dynamic Dark UI radar with flyTo() camera animations    │
   │  - H3 spatial hex danger zones & Top-5 ranked ATM markers   │
   │  - Live Case flow graph & 1-Click Police Dispatch PDF       │
   └─────────────────────────────────────────────────────────────┘
```

### Component Details
* **Frontend (Command Center):** React.js (via Vite), Tailwind CSS (Dark Mode), Mapbox GL JS (spatial H3 hex grids & heatmaps), Recharts (transaction velocity graphs), Zustand (WebSocket real-time state).
* **Backend (Core Logic):** Python, FastAPI (Async), WebSockets (`/live_alerts`), PostgreSQL + PostGIS (spatial queries), SQLAlchemy ORM, JWT Auth & RBAC.
* **Machine Learning Engine:**
  * **WHERE:** H3 Spatial Indexing candidate retrieval -> LightGBM LambdaMART ranking -> SHAP explainability.
  * **WHEN:** `lifelines` (Survival Analysis: Kaplan-Meier / Cox Proportional Hazards).
  * **Fallback Heuristic:** `Score = (Fraud_History * 0.7) + (1/Distance * 0.3)` for cold-start mules.
* **Data Simulation:** Python Faker, pandas, networkx (~200 synthetic ATMs with real coordinates, precomputed distance matrices, 10,000 historical transactions).
* **DevOps:** Docker & Docker Compose for unified one-command startup.

---

## 👥 3. Granular Role Breakdown (Team of 6)

| Role | Focus Area | Key Deliverables |
|---|---|---|
| **Role 1: Backend Engineer** | APIs & Core Logic | SQLAlchemy models, FastAPI endpoints, trigger logic, WebSocket broadcast (`/live_alerts`). |
| **Role 2: ML/AI Engineer** | Predictive Engine | LightGBM LambdaMART ranking, `lifelines` survival time model, SHAP explainability strings, fallback heuristic. |
| **Role 3: Frontend Engineer** | Maps & GIS Radar | Mapbox GL JS dark theme, WebSocket consumer, `map.flyTo()` animations, H3 hex grid overlays, custom markers. |
| **Role 4: Frontend Engineer** | UI/UX & Dashboard | Tailwind dark layout, Live Case Flow visualizer, Top-5 ranking cards, 1-Click Police Dispatch PDF, Confirmed/False Alarm actions. |
| **Role 5: Data Engineer** | Synthetic World Builder | `atms_master.csv`, pre-computed Distance Matrix, `historical_transactions.csv`, `run_live_demo.py` presentation trigger. |
| **Role 6: Integrator & Pitch** | DevOps & System Stability | `docker-compose.yml`, CORS configuration, E2E latency optimization (< 2 sec), presentation deck and demo flow. |

---

## 📂 4. Project Organization & Repositories

Recommended microservices structure under GitHub Organization [`project-drishti-sih26`](https://github.com/project-drishti-sih26):

1. **`frontend-dashboard`**: React/Vite dashboard, Mapbox GL JS radar, Zustand, Tailwind.
2. **`backend-api`**: FastAPI async server, WebSocket handlers, SQLAlchemy models, PostGIS integration.
3. **`ml-engine`**: WHERE & WHEN inference pipelines, LightGBM models, SHAP explanations.
4. **`simulation-data`**: Synthetic fraud graph generation, ATM coordinates, precomputed distance matrix, demo driver.

*(Or unified as a monorepo during initial hackathon sprints).*

---

## 🚀 5. Quick Start (Local Setup)

```bash
# Clone the repository
git clone git@github.com:project-drishti-sih26/project-drishti.git
cd project-drishti

# Spin up services via Docker Compose
docker-compose up --build
```
