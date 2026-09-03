# 🎯 Project Drishti — SIH 2026 Presentation & Pitch Playbook

> **Mission:** Proactive Tactical Intelligence Radar for Cybercrime Interception  
> **Problem Statement ID:** SIH 2026 / Cybercrime & Law Enforcement  
> **Target Audience:** Smart India Hackathon Judges, Senior IPS Officers, Cyber Cell Evaluators

---

## ⚡ 1. The 30-Second Elevator Pitch (Hook)

> *"Honorable Judges, today when a citizen loses ₹1,50,000 to an APK screen-share scam, our policing is **100% reactive**. By the time the FIR is registered on the NCRP portal, scammers have already routed the money across 3 mule accounts and withdrawn physical cash at an ATM. The money is gone.*  
>  
> *We built **Project Drishti** — India's first **proactive cashout forecasting radar**. The moment stolen funds hit a flagged mule account, Drishti predicts **WHERE** the runner is heading (Top-5 ranked physical ATMs) and **WHEN** they will withdraw (exact time window: e.g. in 22–49 minutes). We give local police a **20-minute operational window** to physically catch the runner red-handed."*

---

## 🖥️ 2. The 3-Minute Live Demo Script (Step-by-Step)

### Step 1: Show the Command Dashboard
* Open `frontend/ui_ux/index.html` (or `http://localhost:3000`).
* Point out:
  1. **Left Panel (Money Trail):** Victim account ➔ Intermediary Mule cascade with debit timestamps.
  2. **Center Radar:** Live MapLibre GL spatial map showing Delhi NCR commercial corridors and H3 danger hexagons.
  3. **Right Panel:** Top-5 candidate ATMs with ETA and risk score.

### Step 2: Inject Live Cyber Fraud in Terminal
* Open terminal and execute:
  ```bash
  python simulation/run_live_demo.py
  ```
* Judges will see:
  - 3 legitimate transactions passing quietly.
  - **ALERT!** High-value ₹1,50,000 transfer from `VICTIM-001` to `MULE-X99`.
  - Terminal logs show: **LambdaMART ranking 166 ATMs**, calculating travel time via road matrix, and **Survival Analysis predicting 22-min intercept window**.

### Step 3: Show the Instant Dashboard Reaction
* Without refreshing the browser, the WebSocket fires:
  - Top emergency banner flashes **RED** with live countdown timer.
  - Map smoothly zooms (`flyTo`) onto the **Rank #1 ATM Hotspot** with a pulsing red beacon.
  - Explanations appear: *"Extremely close proximity (~3 min travel) + 10 confirmed past fraud incidents"*.

### Step 4: Click the "1-Click Police Dispatch Order" Button
* Click **[ Generate Police Dispatch Order ]**.
* A formal, legal Section 91 CrPC notice PDF downloads immediately with the suspect account, ranked ATM addresses, and patrol vehicle assignment!

---

## 🛡️ 3. Top Judge Questions & Bulletproof Defense Strategy (FAQ)

### Q1: *"How do you handle a 'Cold Start' if the mule account is brand new and has zero transaction history?"*
* **Evaluation Angle:** Testing if your model blindly overfits to historical account IDs.
* **Winning Defense:**
  > *"Our WHERE engine employs an autonomous **two-stage fallback hierarchy**. If an incoming transaction involves a brand new mule account with zero prior banking history, the pipeline dynamically shifts from LambdaMART to our mathematically calibrated domain fallback (`fallback_heuristic.py`).  
  > In this mode, ranking is computed purely from **immediate physical road reachability** ($1 / \text{distance}$) and the **static historical fraud density of the surrounding ATMs** ($\text{fraud\_count} \times 0.70$). This requires **zero historical user data** while still isolating the top physical risk nodes in under 80 milliseconds."*

### Q2: *"Running live map routing for 100,000 ATMs across India will crash your backend. How is this actually 'real-time'?"*
* **Evaluation Angle:** Testing real-world scalability and computational complexity ($O(N)$ vs $O(1)$).
* **Winning Defense:**
  > *"We never compute dynamic Dijkstra or OSMnx graph pathfinding at inference time. Our architecture solves this in two layers:  
  > 1. **Spatial Pruning (Uber H3 Indexing):** Using H3 hexagonal partitioning at Resolution 9 with a 10% boundary buffer, we instantly prune 100,000 ATMs down to only the ~150 candidates within the perpetrator's reachable perimeter.  
  > 2. **Precomputed Distance Tensor ($O(1)$ Lookup):** Our data pipeline precomputes an offline road travel matrix (`distance_matrix.json`). Live inference simply performs instantaneous **$O(1)$ hash-map lookups** for road distance and travel times, ensuring sub-second end-to-end latency from bank ingestion to police dispatch."*

### Q3: *"Why did you use Learning-to-Rank (LightGBM LambdaMART) instead of a standard binary classifier (Fraud vs. Not Fraud)?"*
* **Evaluation Angle:** Testing ML maturity, metric selection, and loss function understanding.
* **Winning Defense:**
  > *"A standard binary classifier falls directly into the **extreme class imbalance trap**. In any given metropolitan sector with 200 physical ATMs, at the moment of cashout, **199 are 'Not Fraud' and only 1 is 'Fraud'** (a 99.5% class imbalance). A traditional binary classifier will trivially predict 0 for every ATM and achieve **99.5% accuracy while catching zero criminals**.  
  > We formulated cashout prediction as a **Learning-to-Rank (LTR) query optimization problem**, optimizing directly for **Normalized Discounted Cumulative Gain (NDCG@5)**. Instead of predicting an arbitrary probability threshold, LambdaMART scores and orders the candidate ATMs relatively, guaranteeing police receive the **Top-5 most actionable physical targets** every single time."*

### Q4: *"How does the WHEN engine calculate the time window?"*
* **Winning Defense:**
  > *"We use **Kaplan-Meier Survival Analysis**. Standard linear or Poisson regression fails because uncaught frauds or cases where the runner was stopped at transit represent **statistically right-censored data** ($T > t$). Our survival function models the time-to-event probability distribution $S(t) = P(T > t)$, allowing us to construct a mathematically sound 95% confidence interval for the physical cashout arrival window."*

---

## 🚀 4. Technical Architecture Recap

```
[ Banking Core / NPCI Feed ]
              │ (POST /api/v1/transactions)
              ▼
[ FastAPI Backend (Role 1) ] ── (DB Query AccountType.MULE)
              │
              ▼
[ ML Engine (Role 2) ]
  ├── 1. Spatial Filter (H3 Resolution 9 + 10% Edge Buffer)
  ├── 2. LambdaMART Ranker (LightGBM on 11 behavioral features)
  ├── 3. Survival Time (Kaplan-Meier time-to-event window)
  └── 4. SHAP Direction-Aware Explainability
              │
              ▼ (Broadcast JSON)
[ WebSocket /ws/live_alerts ]
              │
              ▼
[ Tactical Command Center (Roles 3 & 4) ]
  ├── MapLibre GL + OpenFreeMap (Zero-token Vector Radar)
  ├── Live Countdown Timer & Hotspot flyTo()
  └── 1-Click PDF Section 91 CrPC Dispatch Order
```
