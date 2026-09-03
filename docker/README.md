# 🚀 Role 6: Integrator & Pitch Strategist (DevOps / QA / Pitch)

## 📌 Ownership
* **Owner:** Integrator & Pitch Strategist (Role 6)
* **Stack:** Docker, Docker Compose, Nginx, PostgreSQL/PostGIS, GitHub Actions, PowerPoint / Pitch Deck.

---

## 📂 Folder Structure
```
docker/
├── Dockerfile.backend      # Backend production build
├── Dockerfile.frontend     # Frontend multi-stage Nginx build
└── README.md               # DevOps instructions
```

---

## 🎯 Deliverables & Key Tasks
1. **Docker Orchestration (`docker-compose.yml`):**
   - Single command `docker-compose up --build` spins up:
     - `postgres` (with PostGIS extension enabled)
     - `backend` (FastAPI + WebSockets on port 8000)
     - `frontend` (Vite / Nginx on port 5173 / 3000)
2. **CORS & Environment Setup (`.env.example`):**
   - Ensure seamless communication between Frontend and Backend with zero CORS errors on presentation laptops.
3. **End-to-End Latency Guarantee:**
   - Verify that from the moment Role 5 presses `ENTER` on `run_live_demo.py`, to the moment Role 3's Mapbox radar animates and Role 4's top-5 cards light up, the total latency is **under 2 seconds**.
4. **Pitch Deck & Presentation Script (`docs/demo_script.md`):**
   - Align presentation strictly with the SIH judging rubric: Innovation, Technical Complexity, Practical Feasibility, and I4C Law Enforcement Impact.
