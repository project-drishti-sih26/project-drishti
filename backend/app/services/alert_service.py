"""
FILE: backend/app/services/alert_service.py
ROLE: Role 1 — Backend Engineer

WebSocket fan-out for live prediction alerts.

WHY THIS ISN'T A THREE-LINE BROADCAST
-------------------------------------
The original implementation iterated the connection list and called
`send_text` directly. If any single client had gone away (closed laptop lid,
Wi-Fi drop, browser refresh), that call raised — and because the exception
escaped the loop, EVERY CLIENT AFTER IT IN THE LIST SILENTLY MISSED THE ALERT.
It also mutated nothing, so dead sockets accumulated forever and the failure got
worse with every reconnect.

In a live demo this presents as "the second judge's screen never updated", and in
production it means an alert that was generated but never delivered. So:
  * each send is isolated — one dead client cannot starve the others
  * dead sockets are collected and removed after the iteration completes
  * we iterate a snapshot, because we mutate the list during cleanup
  * the last alert is retained so a dashboard connecting mid-demo immediately
    renders state instead of an empty screen
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # Replayed to any client that connects after an alert has already fired.
        self.last_alert: Optional[str] = None
        self.alerts_broadcast = 0
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, replay_last: bool = True):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"[AlertService] Client connected. Active: {len(self.active_connections)}")

        # A dashboard opened after the trigger fired would otherwise sit blank
        # until the next transaction — bad in a demo, worse on a shift handover.
        if replay_last and self.last_alert:
            try:
                await websocket.send_text(self.last_alert)
                print("[AlertService] Replayed most recent alert to new client.")
            except Exception:
                pass

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[AlertService] Client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """
        Sends `message` to every connected client. One failing client never
        prevents delivery to the rest.
        """
        self.last_alert = message
        self.alerts_broadcast += 1

        if not self.active_connections:
            print("[AlertService] WARNING: alert generated but NO dashboard is "
                  "connected. It is cached and will replay on next connect.")
            return 0

        dead: List[WebSocket] = []
        delivered = 0
        for connection in list(self.active_connections):   # snapshot: we mutate below
            try:
                await connection.send_text(message)
                delivered += 1
            except Exception as e:
                print(f"[AlertService] Client send failed ({type(e).__name__}) - dropping it.")
                dead.append(connection)

        for d in dead:
            self.disconnect(d)

        print(f"[AlertService] Alert delivered to {delivered}/{delivered + len(dead)} client(s).")
        return delivered

    async def broadcast_json(self, payload: Dict[str, Any]):
        return await self.broadcast(json.dumps(payload, default=str))

    def stats(self) -> Dict[str, Any]:
        return {
            "active_connections": len(self.active_connections),
            "alerts_broadcast": self.alerts_broadcast,
            "has_cached_alert": self.last_alert is not None,
        }


manager = ConnectionManager()
