# 🚀 PROJECT DRISHTI — DEPLOYMENT & EXECUTION GUIDE

> **Proactive Predictive Intelligence Radar for Cybercrime & Mule Account Interception**  
> *Problem Statement:* **SIH26184** | *Partner Agency:* **Indian Cybercrime Coordination Centre (I4C), MHA**

---

## 📑 Table of Contents
1. [System Architecture & Folder Roles](#-1-system-architecture--folder-roles)
2. [Prerequisites & System Requirements](#-2-prerequisites--system-requirements)
3. [Method 1: 1-Click Docker Deployment (Recommended)](#-3-method-1-1-click-docker-deployment-recommended)
4. [Method 2: Local Bare-Metal / Manual Deployment (Without Docker)](#-4-method-2-local-bare-metal--manual-deployment-without-docker)
5. [Method 3: Cloud Production Deployment (AWS / Render / Vercel)](#-5-method-3-cloud-production-deployment-aws--render--vercel)
6. [Live Hackathon Presentation / Demo Flow](#-6-live-hackathon-presentation--demo-flow)
7. [Automated End-to-End Verification](#-7-automated-end-to-end-verification)
8. [Troubleshooting & Common Pitfalls](#-8-troubleshooting--common-pitfalls)

---

## 🏗️ 1. System Architecture & Folder Roles

Project Drishti runs as a unified reactive spatial-temporal radar pipeline. Below is how all folders interact during deployment:

```
                          ┌───────────────────────────────────────┐
                          │   SIMULATION (Jury Demo Trigger)      │
                          │   simulation/run_live_demo.py         │
                          └──────────────────┬────────────────────┘
                                             │ HTTP POST (₹1,25,000 mule txn)
                                             ▼
                          ┌───────────────────────────────────────┐
                          │       BACKEND API (FastAPI)           │
                          │   backend/app/main.py (:8000)         │
                          └──────────┬─────────────────┬──────────┘
                                     │                 │
              In-process Zero-IPC    │                 │ Spatial queries
                                     ▼                 ▼
          ┌──────────────────────────────────┐   ┌────────────────────────┐
          │      ML DUAL-ENGINE INFERENCE    │   │  POSTGRESQL + POSTGIS  │
          │  ml_engine/pipelines/            │   │  (:5432) or SQLite     │
          │  - WHERE: LightGBM LambdaMART    │   └────────────────────────┘
          │  - WHEN: Lifelines Cox Survival  │
          │  - EXPLAIN: SHAP Attributions    │
          └──────────────────┬───────────────┘
                             │
                             ▼ Broadcast alert JSON (<2 sec)
                 WebSocket: /ws/live_alerts
                             │
                             ▼
          ┌────────────────────────────────────────────────────────┐
          │        FRONTEND TACTICAL COMMAND RADAR                 │
          │   frontend/ (React 18 + Vite + MapLibre GL) (:5173)    │
          │   - Live Case Flow & Victim Details                    │
          │   - Dynamic Dark Mapbox/OSM Radar with H3 Hexes        │
          │   - Ranked Top-5 Candidate ATMs & Police Dispatch PDF  │
          └────────────────────────────────────────────────────────┘
```

### Folder Breakdown & Deployment Purpose

| Directory | Core Stack | Deployment Role |
|---|---|---|
| **`docker-compose.yml`** | Docker Compose | Master multi-container orchestrator (Postgres, Backend, Frontend). |
| **`backend/`** | FastAPI, Uvicorn, SQLAlchemy | REST API, WebSocket server, database models, and trigger service on port `8000`. |
| **`frontend/`** | React 18, Vite, MapLibre GL, Tailwind | Real-time tactical radar command dashboard on port `5173`. |
| **`ml_engine/`** | LightGBM, Lifelines, SHAP | Dual-engine AI brain. Imported directly in-process by the backend for sub-second prediction latency. |
| **`simulation/`** | Python, Requests | Live fraud transaction injector for jury demonstration (`run_live_demo.py`). |
| **`docs/`** | Markdown | Pitch script (`SIH_PITCH_PLAYBOOK.md`) and E2E verification proof (`PITCH_VERIFIED.md`). |
| **`verify_e2e.py`** | Python | Automated 26-point end-to-end integration test harness. |

---

## 📋 2. Prerequisites & System Requirements

Ensure the following tools are installed on the deployment machine:

- **Docker Desktop** (v20+ with Docker Compose v2+) — *Required for Method 1*
- **Python 3.11+** — *Required for local execution*
- **Node.js 18+ & npm 9+** — *Required for local frontend*
- **Port Availability:**
  - `5173` (Frontend UI)
  - `8000` (Backend API & WebSockets)
  - `5432` (PostgreSQL Database)

---

## ⚡ 3. Method 1: 1-Click Docker Deployment (Recommended)

This is the standard, containerized deployment designed for presentation laptops and hackathon judging environments to eliminate "works on my machine" issues.

### Step 1: Clone Repository & Enter Root
```bash
git clone git@github.com:project-drishti-sih26/project-drishti.git
cd project-drishti
```

### Step 2: Environment Configuration
Copy the provided environment template:
```bash
# Windows PowerShell
copy .env.example .env

# Linux / macOS / Git Bash
cp .env.example .env
```

### Step 3: Build & Launch Stack
```bash
docker-compose up --build
```
*(To run in background detached mode, use `docker-compose up -d --build`)*

### Container Health & Access Endpoints
Once running, verify the services:

| Service | Container Name | URL / Port | Purpose |
|---|---|---|---|
| **Frontend Radar** | `drishti_frontend` | [http://localhost:5173](http://localhost:5173) | Command Center UI |
| **FastAPI Backend** | `drishti_backend` | [http://localhost:8000](http://localhost:8000) | Root API health status |
| **Swagger Docs** | `drishti_backend` | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API documentation |
| **Live WebSocket** | `drishti_backend` | `ws://localhost:8000/ws/live_alerts` | Real-time alert stream |
| **PostgreSQL DB** | `drishti_db` | `localhost:5432` | PostGIS spatial database |

### Step 4: Stop Containers
To shut down the entire stack cleanly:
```bash
docker-compose down
```

---

## 🛠️ 4. Method 2: Local Bare-Metal / Manual Deployment (Without Docker)

Use this method for rapid development or if Docker is not available on the presentation machine.

### Step 1: Database Setup & Seeding
If PostgreSQL is not running locally, Project Drishti automatically falls back to SQLite (`drishti.db`). Seed the initial ATM locations and mule accounts:
```bash
python backend/db/seed_data.py
```

### Step 2: Deploy Backend & ML Engine
Open **Terminal 1** in the project root:
```bash
# 1. Install backend + ML runtime dependencies
pip install -r backend/requirements.txt

# 2. Start the FastAPI server (run from project root so ml_engine is in PYTHONPATH)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Healthcheck:* Open [http://localhost:8000/docs](http://localhost:8000/docs) to confirm the API is active.

### Step 3: Deploy Frontend Dashboard
Open **Terminal 2** in the project root:
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install NPM dependencies
npm install

# 3. Launch Vite development server
npm run dev
```
*Access UI:* Open [http://localhost:5173](http://localhost:5173) in Chrome or Edge.

---

## ☁️ 5. Method 3: Cloud Production Deployment (AWS / Render / Vercel)

If hosting the system live on cloud infrastructure:

### Architecture Split
1. **Managed Database (PostgreSQL + PostGIS):**
   - Deploy on **Supabase**, **Neon**, or **AWS RDS PostgreSQL** with PostGIS enabled (`CREATE EXTENSION postgis;`).
   - Set the connection string in your production environment:
     ```env
     DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<dbname>
     ```

2. **Backend & ML Engine Service (FastAPI + WebSockets):**
   - Deploy on **AWS EC2**, **DigitalOcean Droplet**, or **Render.com** (Web Service).
   - Because `backend/` imports `ml_engine/` locally for zero-IPC latency, deploy the entire repository root with the start command:
     ```bash
     uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2
     ```
   - Ensure inbound port `8000` (or `443` reverse-proxied via Nginx) allows WebSocket upgrades (`Upgrade: websocket`).

3. **Frontend Dashboard (React + Vite):**
   - Deploy on **Vercel**, **Netlify**, or **Cloudflare Pages**.
   - Build Settings:
     - **Root Directory:** `frontend`
     - **Build Command:** `npm run build`
     - **Output Directory:** `dist`
   - Environment Variables:
     ```env
     VITE_API_URL=https://api.yourdomain.com
     VITE_WS_URL=wss://api.yourdomain.com/ws/live_alerts
     ```

---

## 🎯 6. Live Hackathon Presentation / Demo Flow

Follow this exact sequence during jury evaluation:

1. **Screen 1 (Command Center):**  
   Open [http://localhost:5173](http://localhost:5173) on the main display. Show the radar map in idle standby with live status indicator.
2. **Screen 2 / Terminal (The Fraud Trigger):**  
   Open a separate terminal window and execute:
   ```bash
   python simulation/run_live_demo.py
   ```
3. **The Immediate Reaction (< 2 Seconds):**
   - Terminal outputs: `✅ Alert successfully broadcasted to FastAPI backend`
   - Frontend Command Center triggers a high-priority red alert: **"CRITICAL FRAUD EVENT DETECTED"**.
   - Map automatically zooms (`flyTo()`) to the high-probability interception hotspot.
   - H3 spatial danger hexes illuminate on the radar.
   - Right sidebar renders the **Top-5 Ranked Candidate ATMs** with travel times and SHAP explainability.
   - Center banner displays the **Survival Analysis Cashout Window** (e.g., *"Cashout expected in 25–40 minutes"*).
4. **Dispatch Proof:**  
   Click **"Export Police Dispatch PDF"** to demonstrate instant field-readiness for patrol interception.

---

## 🧪 7. Automated End-to-End Verification

Before presenting, run the automated 26-point verification suite to prove the system works:

```bash
python verify_e2e.py
```

### What `verify_e2e.py` Validates:
- [x] Backend HTTP root & `/docs` availability
- [x] WebSocket client connection to `/ws/live_alerts`
- [x] Fraud transaction injection thresholding (₹50,000+ mule trigger)
- [x] WHERE engine spatial candidate pruning and LightGBM ranking
- [x] WHEN engine survival analysis cumulative hazard window
- [x] Real-time WebSocket broadcast latency (< 2000 ms)
- [x] SHAP feature attribution explainability

---

## 🔧 8. Troubleshooting & Common Pitfalls

### 1. Port Conflict (`Port 8000 or 5173 already in use`)
Find and terminate the process occupying the port:
```powershell
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Linux / macOS
lsof -ti:8000 | xargs kill -9
```

### 2. ML Engine Import Error (`ModuleNotFoundError: No module named 'ml_engine'`)
Ensure you run commands from the **project workspace root**, or set `PYTHONPATH`:
```powershell
# Windows PowerShell
$env:PYTHONPATH = "."
uvicorn backend.app.main:app --port 8000 --reload

# Linux / macOS
export PYTHONPATH=.
uvicorn backend.app.main:app --port 8000 --reload
```

### 3. WebSocket Disconnected / No Live Alerts on UI
- Verify backend is running on `http://localhost:8000`.
- Check browser console (`F12`) to verify WebSocket connected to `ws://localhost:8000/ws/live_alerts`.
- If running across different network devices, update `frontend/.env` to point `VITE_API_URL` and `VITE_WS_URL` to your host machine's LAN IP.

---

<div align="center">
  <b>Project Drishti — Smart India Hackathon (SIH 2026)</b><br />
  <i>Team Project Drishti</i>
</div>
