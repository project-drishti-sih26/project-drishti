import json
from sqlalchemy.orm import Session
from app.services.alert_service import manager
from app.ml_bridge.inferencer import calculate_top_atms
from app.schemas.transaction import TransactionCreate

async def evaluate_transaction(tx: TransactionCreate, db: Session):
    if tx.receiver_id.startswith("MULE"):
        payload = calculate_top_atms(tx.receiver_id, db)
        await manager.broadcast(json.dumps(payload))
        return True
    return False
