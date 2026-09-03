# ⚙️ Role 1: Backend Engineer (APIs & Core Logic)

## 📌 Ownership
* **Owner:** Backend Engineer (Role 1)
* **Stack:** Python 3.11+, FastAPI (Async), PostgreSQL with PostGIS, SQLAlchemy, WebSockets, Pydantic.

---

## 📂 Folder Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/       # Route handlers (transactions.py, cases.py, websockets.py)
│   │   └── router.py        # Master API router
│   ├── core/                # Configuration (config.py, security.py)
│   ├── db/                  # Session & DB initialization (session.py, base.py)
│   ├── models/              # SQLAlchemy models (Account, Transaction, PhysicalLocation, Case)
│   ├── schemas/             # Pydantic input/output validation schemas
│   └── services/            # Core business logic & ML trigger (trigger_service.py, alert_service.py)
├── Dockerfile               # Backend container configuration
├── requirements.txt         # Python dependencies
└── README.md                # This guide
```

---

## 🎯 Deliverables & Key Tasks
1. **Database Models (`app/models/`):**
   - Translate the SQL schema from [PROJECT_BLUEPRINT.md](../PROJECT_BLUEPRINT.md#5-complete-database-schema-sqlalchemy-reference) into modular SQLAlchemy models (`Account`, `Transaction`, `PhysicalLocation`, `Case`).
2. **Data Ingestion API (`app/api/endpoints/transactions.py`):**
   - `POST /api/v1/transactions`: Ingest simulated transactions pushed by the Data Engineer (Role 5).
3. **Trigger Logic (`app/services/trigger_service.py`):**
   - Condition: `If incoming_amount > ₹50,000 AND account_type == "Mule" -> Trigger ML Engine`.
4. **Real-time WebSockets (`app/api/endpoints/websockets.py`):**
   - Expose `ws://.../live_alerts` to stream real-time prediction payloads to the Frontend (Roles 3 & 4).
5. **CORS & Integration:**
   - Configure CORS middleware allowing the React Vite frontend (`http://localhost:5173`).
