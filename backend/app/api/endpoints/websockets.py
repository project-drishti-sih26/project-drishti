"""
FILE: backend/app/api/endpoints/websockets.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the WebSocket endpoint that the React Frontend connects
    to for receiving real-time fraud prediction alerts. This is the "live wire"
    of Project Drishti — when a prediction is broadcast, it appears here
    and gets pushed to the browser in milliseconds.

📌 WHY IS THIS FILE NEEDED?
    HTTP polling (asking the server every second "any new alerts?") would
    create unnecessary load and introduce latency. WebSockets maintain a
    persistent bidirectional connection, so the moment a prediction is ready,
    the server PUSHES it to the browser instantly.
    This is what achieves the < 2 second end-to-end latency requirement
    that Role 6 must verify.

📌 WHAT TO IMPLEMENT HERE:

    1. THE WEBSOCKET ENDPOINT ROUTE:
       router = APIRouter(tags=["WebSocket"])

       @router.websocket("/ws/live_alerts")
       async def websocket_live_alerts(websocket: WebSocket):
           """
           This function handles the lifecycle of a single WebSocket connection:

           Step 1: Register the connection.
               await manager.connect(websocket)

           Step 2: Keep the connection alive in a loop.
               Use try/except to handle disconnection gracefully.

               try:
                   while True:
                       # Wait for any message from client (optional heartbeat)
                       # We can receive a "ping" text from frontend to keep alive
                       data = await websocket.receive_text()

                       # Optional: If client sends "PING", respond with "PONG"
                       if data == "PING":
                           await websocket.send_text("PONG")

               except WebSocketDisconnect:
                   # Client closed the browser tab or connection dropped
                   manager.disconnect(websocket)

           The actual prediction data is NOT sent here directly.
           It is sent by alert_service.broadcast_alert() which calls
           manager.broadcast() from alert_service.py.
           """

    2. OPTIONAL — WEBSOCKET STATUS ENDPOINT (HTTP, for debugging):
       @router.get("/ws/status")
       def websocket_status():
           """
           Returns the number of currently connected WebSocket clients.
           Useful for Role 6 to verify frontend clients are connected
           before triggering the demo.
           Returns: {"connected_clients": 2}
           """
           return {"connected_clients": len(manager.active_connections)}

📌 HOW IT CONNECTS TO OTHER FILES:
    - Imports `manager` from services/alert_service.py.
    - This router is registered directly in main.py (NOT via api/router.py
      since WebSocket routes don't use the /api/v1 prefix).
    - Frontend (Roles 3 & 4) connects using:
      `const ws = new WebSocket("ws://localhost:8000/ws/live_alerts")`
      This is defined in frontend/src/services/WebSocketClient.js.

📌 LIBRARIES TO USE:
    - fastapi (APIRouter, WebSocket, WebSocketDisconnect)
    - app.services.alert_service (manager)

📌 IMPORTANT — FRONTEND CONNECTION URL:
    The React frontend should connect to:
    Development: ws://localhost:8000/ws/live_alerts
    Production:  wss://your-domain.com/ws/live_alerts  (note: wss:// for TLS)
    This URL is stored in frontend's .env as VITE_WS_URL.
"""
