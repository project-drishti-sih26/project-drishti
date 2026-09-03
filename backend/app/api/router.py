"""
FILE: backend/app/api/router.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the master API router that assembles all sub-routers (transactions,
    cases, websockets) into one single router that main.py includes.
    Think of it as the "switchboard" — it routes incoming requests to the
    correct endpoint handler file.

📌 WHAT TO IMPLEMENT HERE:
    from fastapi import APIRouter
    from app.api.endpoints import transactions, cases

    api_router = APIRouter()
    api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
    api_router.include_router(cases.router, prefix="/cases", tags=["Cases"])

    NOTE: The WebSocket router in endpoints/websockets.py is registered directly
    in main.py WITHOUT the /api/v1 prefix, because WebSocket URLs should be
    clean (ws://host/ws/live_alerts, not ws://host/api/v1/ws/live_alerts).

📌 HOW IT CONNECTS TO OTHER FILES:
    - main.py: `app.include_router(api_router, prefix=settings.API_V1_STR)`
      This makes all endpoints available at /api/v1/...
"""
