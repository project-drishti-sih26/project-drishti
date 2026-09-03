"""
FILE: backend/app/services/alert_service.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file manages the WebSocket connection hub. It maintains the list of
    all currently connected Frontend clients (Roles 3 & 4's browser tabs),
    and provides the `broadcast_alert()` function that pushes prediction
    JSON to ALL connected clients simultaneously when a fraud is detected.

📌 WHY IS THIS FILE NEEDED?
    HTTP is a request-response protocol — the client asks, server answers.
    We can't "push" data to the frontend over HTTP. WebSockets solve this:
    the frontend connects once and keeps the connection open. When ML fires,
    the backend PUSHES the alert to the frontend in real-time without the
    frontend needing to ask.
    This file manages the set of open WebSocket connections and handles
    broadcasting, disconnection, and errors gracefully.

📌 WHAT TO IMPLEMENT HERE:

    1. CONNECTION MANAGER CLASS:
       class ConnectionManager:
           def __init__(self):
               # A set of all currently active WebSocket connections
               self.active_connections: List[WebSocket] = []

           async def connect(self, websocket: WebSocket):
               # Accept the WebSocket handshake and add to active connections
               await websocket.accept()
               self.active_connections.append(websocket)
               print(f"[WS] New client connected. Total: {len(self.active_connections)}")

           def disconnect(self, websocket: WebSocket):
               # Remove a disconnected client from the list
               self.active_connections.remove(websocket)
               print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

           async def broadcast(self, message: str):
               # Send a text message (JSON string) to ALL connected clients
               # Handle disconnection errors gracefully — if a client disconnected
               # mid-broadcast, catch the error and remove them from the list.
               disconnected = []
               for connection in self.active_connections:
                   try:
                       await connection.send_text(message)
                   except Exception:
                       disconnected.append(connection)
               # Cleanup stale connections after the loop
               for conn in disconnected:
                   self.active_connections.remove(conn)

       # Create a SINGLETON instance that the entire app shares
       manager = ConnectionManager()

    2. BROADCAST HELPER FUNCTION:
       async def broadcast_alert(prediction_data: dict):
           """
           Converts the prediction dict to a JSON string and broadcasts it.
           Called by trigger_service.py after ML prediction completes.
           """
           import json
           message = json.dumps(prediction_data, default=str)  # default=str handles datetime
           await manager.broadcast(message)

📌 HOW IT CONNECTS TO OTHER FILES:
    - api/endpoints/websockets.py imports `manager` to handle the ws:// route.
    - services/trigger_service.py imports `broadcast_alert` to push predictions.
    - The Frontend (Roles 3 & 4) connects to the WebSocket endpoint defined
      in websockets.py, which uses this manager under the hood.

📌 LIBRARIES TO USE:
    - fastapi (WebSocket)
    - typing (List)
    - json

📌 IMPORTANT CONCURRENCY NOTE:
    This simple list-based manager works fine for a single-server hackathon.
    In production, you'd use Redis Pub/Sub to broadcast across multiple
    server instances. For SIH demo, this approach is perfect.
"""
