from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.alert_service import manager

router = APIRouter()

@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
