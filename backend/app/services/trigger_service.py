import json
import os
import sys
from sqlalchemy.orm import Session
from app.services.alert_service import manager
from app.schemas.transaction import TransactionCreate

# Ensure project root is on sys.path so ml_engine can be imported cleanly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

async def evaluate_transaction(tx: TransactionCreate, db: Session):
    is_mule = tx.receiver_id.startswith("MULE") or (tx.amount and tx.amount >= 50000)
    if is_mule:
        payload = None
        # Try real ML Engine inference pipeline first
        try:
            from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout
            payload = predict_fraud_cashout({
                "mule_account_id": tx.receiver_id,
                "transaction_amount": float(tx.amount),
                "transaction_timestamp": str(tx.timestamp or ""),
                "victim_account_id": tx.sender_id,
            })
            print(f"[TriggerService] ML Engine generated prediction alert: {payload.get('alert_id')}")
        except Exception as e:
            print(f"[TriggerService] ML Engine fallback invoked: {e}")
            from app.ml_bridge.inferencer import calculate_top_atms
            payload = calculate_top_atms(tx.receiver_id, db)

        if payload:
            await manager.broadcast(json.dumps(payload, default=str))
        return True
    return False
