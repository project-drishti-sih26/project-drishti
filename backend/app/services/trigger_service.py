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

from app.models.account import Account, AccountType

async def evaluate_transaction(tx: TransactionCreate, db: Session):
    # Query database to check if receiver account is a confirmed Mule
    account = db.query(Account).filter(Account.account_id == tx.receiver_id).first()
    
    is_mule_account = account is not None and account.account_type == AccountType.MULE
    is_demo_mule = (
        tx.receiver_id.startswith("MULE") or
        "MULE" in tx.receiver_id.upper() or
        (getattr(tx, "account_type", None) and str(tx.account_type).upper() == "MULE")
    )
    meets_amount = tx.amount is not None and tx.amount >= 50000.0

    # Trigger ML if DB confirms Mule account or demo mule ID, and amount threshold is met
    if (is_mule_account and meets_amount) or (is_demo_mule and meets_amount):
        payload = None
        mule_lat = getattr(tx, "last_known_lat", None) or (account.last_known_latitude if account and account.last_known_latitude else None)
        mule_lon = getattr(tx, "last_known_lon", None) or (account.last_known_longitude if account and account.last_known_longitude else None)

        # Try real ML Engine inference pipeline first
        try:
            from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout
            payload = predict_fraud_cashout({
                "mule_account_id": tx.receiver_id,
                "last_latitude": mule_lat,
                "last_longitude": mule_lon,
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
