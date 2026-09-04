"""
FILE: backend/app/services/trigger_service.py
ROLE: Role 1 — Backend Engineer

The decision point: does this incoming transaction warrant a predictive alert?

TRIGGER LOGIC
-------------
Fire when the receiving account is a known/suspected mule AND the amount clears
the reporting threshold. Both conditions matter: mule accounts also receive small
legitimate-looking amounts, and large transfers between clean accounts are not
our problem. ₹50,000 aligns with the amount band at which cyber-fraud cases are
formally registered and a patrol response is proportionate.

ON THE FALLBACK PATH — READ THIS BEFORE CHANGING IT
---------------------------------------------------
If the ML engine raises, we fall back to a heuristic. That fallback previously
produced RANDOM distances (`random.uniform(1.0, 15.0)`) and the payload was
broadcast with no indication it was synthetic. A dashboard cannot distinguish it
from a real prediction, so a silent ML failure would put an officer in a car
heading to a randomly-chosen ATM while the screen showed full confidence.

Every fallback payload is therefore stamped with `degraded: True` and a
`degraded_reason`, so the UI can and must show that it is not a real prediction.
Failing loudly is the only safe behaviour here.
"""

import json
import os
import sys
import traceback

from sqlalchemy.orm import Session

from app.schemas.transaction import TransactionCreate
from app.services.alert_service import manager

# Ensure project root is importable so `ml_engine` resolves.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.models.account import Account, AccountType  # noqa: E402

AMOUNT_THRESHOLD = 50000.0


def _resolve_mule_location(tx: TransactionCreate, account):
    """
    Last known position of the mule, preferring what the transaction carried
    (freshest) over the stored account record.

    Note `is not None` rather than truthiness: latitude 0.0 is a valid
    coordinate, and `or` would discard it.
    """
    lat = getattr(tx, "last_known_lat", None)
    lon = getattr(tx, "last_known_lon", None)
    if lat is None and account is not None:
        lat = getattr(account, "last_known_latitude", None)
    if lon is None and account is not None:
        lon = getattr(account, "last_known_longitude", None)
    return lat, lon


async def evaluate_transaction(tx: TransactionCreate, db: Session) -> bool:
    """
    Evaluates one transaction and, if it qualifies, runs the ML engine and
    broadcasts the resulting alert.

    Returns True if the predictive pipeline was triggered.
    """
    account = db.query(Account).filter(Account.account_id == tx.receiver_id).first()

    is_mule_account = account is not None and account.account_type == AccountType.MULE
    is_demo_mule = (
        "MULE" in tx.receiver_id.upper()
        or (getattr(tx, "account_type", None) and str(tx.account_type).upper() == "MULE")
    )
    meets_amount = tx.amount is not None and tx.amount >= AMOUNT_THRESHOLD

    if not (meets_amount and (is_mule_account or is_demo_mule)):
        return False

    # A mule-to-mule hop (tier 2) means the syndicate is already layering, which
    # empirically cashes out faster — the survival model uses this covariate.
    sender = db.query(Account).filter(Account.account_id == tx.sender_id).first()
    mule_tier = 2 if (sender is not None and sender.account_type == AccountType.MULE) else 1

    mule_lat, mule_lon = _resolve_mule_location(tx, account)
    if mule_lat is None or mule_lon is None:
        print("[TriggerService] WARNING: no last-known location for "
              f"{tx.receiver_id} — spatial precision will be degraded.")

    # Case ID derived from the transaction so an alert is traceable back to the
    # transfer that caused it. A random ID per alert breaks the audit trail.
    case_id = getattr(tx, "case_id", None) or f"CYB-{tx.tx_id}"

    payload = None
    try:
        from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout
        payload = predict_fraud_cashout({
            "mule_account_id": tx.receiver_id,
            "victim_account_id": tx.sender_id,
            "last_latitude": mule_lat,
            "last_longitude": mule_lon,
            "transaction_amount": float(tx.amount),
            "transaction_timestamp": (tx.timestamp.isoformat() if tx.timestamp else ""),
            "case_id": case_id,
            "mule_tier": mule_tier,
        })
        payload["degraded"] = False
        print(f"[TriggerService] ML alert generated: {payload.get('alert_id')} "
              f"({payload.get('model_used')})")
    except Exception as e:
        # Print the traceback: a swallowed stack trace during a live demo means
        # nobody can tell whether the ML engine is broken or merely unavailable.
        print(f"[TriggerService] ML ENGINE FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        try:
            from app.ml_bridge.inferencer import calculate_top_atms
            payload = calculate_top_atms(tx.receiver_id, db)
            if payload:
                payload["degraded"] = True
                payload["degraded_reason"] = (
                    f"ML engine unavailable ({type(e).__name__}). "
                    "Showing a database heuristic, NOT a model prediction."
                )
                payload.setdefault("model_used", "DegradedHeuristic")
                print("[TriggerService] Serving DEGRADED heuristic payload (flagged in UI).")
        except Exception as e2:
            print(f"[TriggerService] Fallback also failed: {e2}")
            payload = None

    if payload:
        await manager.broadcast(json.dumps(payload, default=str))
        return True

    print("[TriggerService] No payload produced - nothing broadcast.")
    return False
