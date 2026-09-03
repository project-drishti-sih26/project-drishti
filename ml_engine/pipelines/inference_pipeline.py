"""
Project Drishti — ML Engine
File: ml_engine/pipelines/inference_pipeline.py
Role: Role 2 — ML/AI Engineer

MASTER ENTRYPOINT of the ML Engine.
The Backend (trigger_service.py) calls ONE function: predict_fraud_cashout()
and gets back a fully-structured prediction payload.

Internal pipeline:
    STEP 1 → Spatial Filter    (WHERE: get reachable ATM candidates)
    STEP 2 → Ranker            (WHERE: score & rank candidates)
    STEP 3 → Survival Time     (WHEN: predict withdrawal time window)
    STEP 4 → Explainability    (WHY: generate plain-English reasons)
    STEP 5 → Assemble Payload  (Package into PredictionAlert JSON)
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

# ─── ML sub-module imports ────────────────────────────────────────────────────
from ml_engine.pipelines.spatial_filter import get_candidate_atms
from ml_engine.models.fallback_heuristic import score_candidates_heuristic
from ml_engine.models.survival_time import predict_time_window
from ml_engine.pipelines.explainability import generate_explanations

# LambdaMART ranker (imported lazily — only when model file exists)
_ltr_ranker_available = False
try:
    from ml_engine.models.ltr_ranker import rank_atm_candidates, ModelNotTrainedError
    _ltr_ranker_available = True
except ImportError:
    pass

# ─── Config ───────────────────────────────────────────────────────────────────
# Delhi center coordinates — used when mule location is unknown
DELHI_CENTER_LAT = 28.6139
DELHI_CENTER_LON = 77.2090
TOP_N = 5   # Always return Top 5 ranked ATMs


def _safe_float(val, default: float = 0.0) -> float:
    """
    Converts any numeric value (numpy.float64, numpy.int64, pandas NA, etc.)
    to a standard Python float safe for json.dumps without default=str.
    This prevents React/Recharts/Mapbox from receiving strings instead of numbers.
    """
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val, default: int = 0) -> int:
    """Same as _safe_float but returns int."""
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def predict_fraud_cashout(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master inference pipeline. Called by backend/app/services/trigger_service.py.

    Args:
        input_data (dict): {
            "mule_account_id":       str,
            "last_latitude":         float | None,
            "last_longitude":        float | None,
            "transaction_amount":    float,
            "transaction_timestamp": str  (ISO format),
            "case_id":               str,
            "victim_account_id":     str,
        }

    Returns:
        dict: Full PredictionAlert payload matching backend/app/schemas/prediction.py
    """
    print(f"\n[Pipeline] Starting inference for case: {input_data.get('case_id')}")
    print(f"[Pipeline] Mule account: {input_data.get('mule_account_id')}")

    # ── Extract inputs ─────────────────────────────────────────────────────
    mule_id      = input_data.get("mule_account_id", "UNKNOWN")
    victim_id    = input_data.get("victim_account_id", "UNKNOWN")
    amount       = float(input_data.get("transaction_amount", 0))
    tx_timestamp = input_data.get("transaction_timestamp", datetime.now(timezone.utc).isoformat())
    case_id      = input_data.get("case_id", f"CASE-{uuid.uuid4().hex[:8].upper()}")

    mule_lat = input_data.get("last_latitude") or DELHI_CENTER_LAT
    mule_lon = input_data.get("last_longitude") or DELHI_CENTER_LON

    if not input_data.get("last_latitude"):
        print("[Pipeline] WARNING: Mule location unknown. Using Delhi center as fallback.")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: SPATIAL FILTER — Get reachable ATM candidates
    # ─────────────────────────────────────────────────────────────────────────
    print("[Pipeline] Step 1: Spatial candidate retrieval...")
    candidates = get_candidate_atms(mule_lat, mule_lon, max_travel_minutes=45)
    total_candidates = len(candidates)
    print(f"[Pipeline] Step 1 complete: {total_candidates} candidates retrieved.")

    if total_candidates == 0:
        print("[Pipeline] CRITICAL: No candidates found! Returning empty prediction.")
        return _build_empty_payload(case_id, mule_id, victim_id, amount, tx_timestamp)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: RANKING — Score and rank candidates (WHERE engine)
    # ─────────────────────────────────────────────────────────────────────────
    print("[Pipeline] Step 2: Ranking candidates...")
    model_used = "FallbackHeuristic"
    ltr_model = None
    feature_matrix = None
    feature_names = None

    if _ltr_ranker_available:
        try:
            ranked_candidates, feature_matrix, feature_names, ltr_model = rank_atm_candidates(
                candidates, mule_id, tx_timestamp
            )
            model_used = "LambdaMART"
            print("[Pipeline] Step 2 complete: LambdaMART ranking applied.")
        except (ModelNotTrainedError, Exception) as e:
            print(f"[Pipeline] LambdaMART not available ({e}). Using heuristic.")
            ranked_candidates = score_candidates_heuristic(candidates)
    else:
        ranked_candidates = score_candidates_heuristic(candidates)
        print("[Pipeline] Step 2 complete: Heuristic fallback ranking applied.")

    # Take the Top N
    top_candidates = ranked_candidates[:TOP_N]

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: SURVIVAL ANALYSIS — Predict cashout time window (WHEN engine)
    # ─────────────────────────────────────────────────────────────────────────
    print("[Pipeline] Step 3: Predicting time window...")
    time_window = predict_time_window(
        transaction_timestamp=tx_timestamp,
        mule_account_id=mule_id,
    )
    print(f"[Pipeline] Step 3 complete: Window {time_window['start']} – {time_window['end']}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: EXPLAINABILITY — Generate plain-English reasons
    # ─────────────────────────────────────────────────────────────────────────
    print("[Pipeline] Step 4: Generating explanations...")
    explanations = generate_explanations(
        top_candidates=top_candidates,
        model=ltr_model,
        feature_matrix=feature_matrix,
        feature_names=feature_names,
        model_used=model_used,
    )
    print("[Pipeline] Step 4 complete.")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: ASSEMBLE PAYLOAD — Build the PredictionAlert JSON
    # ─────────────────────────────────────────────────────────────────────────
    print("[Pipeline] Step 5: Assembling prediction payload...")
    top_5_atms = []
    for i, (atm, explanation) in enumerate(zip(top_candidates, explanations)):
        top_5_atms.append({
            "rank":              i + 1,
            "location_id":       str(atm.get("location_id", f"ATM_UNKNOWN_{i+1}")),
            "bank_name":         str(atm.get("bank_name", "Unknown Bank")),
            # Explicit native float casts — prevents numpy.float64 reaching JSON/WebSocket
            "latitude":          _safe_float(atm.get("latitude")),
            "longitude":         _safe_float(atm.get("longitude")),
            "address":           str(atm.get("address", "Address not available")),
            "distance_km":       _safe_float(atm.get("distance_km")),
            "travel_time_mins":  _safe_float(atm.get("travel_time_mins")),
            # historical_fraud_count may come as numpy.int64 from pandas DataFrame
            "historical_fraud_count": _safe_int(atm.get("historical_fraud_count", 0)),
            "confidence_score":  _safe_float(atm.get("confidence_score", atm.get("score"))),
            "explanation":       str(explanation),
        })

    alert_payload = {
        "alert_id":                   f"ALERT-{uuid.uuid4().hex[:8].upper()}",
        "case_id":                    case_id,
        "mule_account_id":            mule_id,
        "victim_account_id":          victim_id,
        "compromised_amount":         amount,
        "detected_at":                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "time_window":                time_window,
        "top_5_atms":                 top_5_atms,
        "model_used":                 model_used,
        "total_candidates_evaluated": total_candidates,
    }

    print(f"[Pipeline] Prediction complete. Alert ID: {alert_payload['alert_id']}")
    return alert_payload


def _build_empty_payload(case_id, mule_id, victim_id, amount, tx_timestamp) -> Dict:
    """Returns a minimal safe payload when no candidates are found."""
    return {
        "alert_id":                   f"ALERT-EMPTY-{uuid.uuid4().hex[:6].upper()}",
        "case_id":                    case_id,
        "mule_account_id":            mule_id,
        "victim_account_id":          victim_id,
        "compromised_amount":         amount,
        "detected_at":                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "time_window":                {"start": None, "end": None, "minutes_from_now": 0, "confidence": 0.0},
        "top_5_atms":                 [],
        "model_used":                 "NONE",
        "total_candidates_evaluated": 0,
    }


# ─── Self-test (FULL END-TO-END PIPELINE) ─────────────────────────────────────
if __name__ == "__main__":
    test_input = {
        "mule_account_id":       "ACC_MULE_0042",
        "last_latitude":         28.6315,   # Connaught Place, Delhi
        "last_longitude":        77.2167,
        "transaction_amount":    75000.0,
        "transaction_timestamp": datetime.now(timezone.utc).isoformat(),
        "case_id":               "CYB-2026-DL-00001",
        "victim_account_id":     "ACC_VICTIM_0001",
    }

    result = predict_fraud_cashout(test_input)

    print("\n" + "="*65)
    print("  PROJECT DRISHTI — END-TO-END PREDICTION OUTPUT")
    print("="*65)
    print(f"  Alert ID    : {result['alert_id']}")
    print(f"  Case ID     : {result['case_id']}")
    print(f"  Amount      : Rs.{result['compromised_amount']:,.0f}")
    print(f"  Model Used  : {result['model_used']}")
    print(f"  Candidates  : {result['total_candidates_evaluated']}")
    print(f"  Time Window : {result['time_window']['start']} to {result['time_window']['end']}")
    print(f"  Police have : {result['time_window']['minutes_from_now']} minutes to act!")
    print("\n  TOP 5 PREDICTED ATMs:")
    print("-"*65)
    for atm in result["top_5_atms"]:
        print(f"  Rank #{atm['rank']}: {atm['bank_name']} | {atm['address']}")
        print(f"           Travel: {atm['travel_time_mins']} min | "
              f"Score: {atm['confidence_score']:.3f}")
        print(f"           {atm['explanation']}")
        print()

    # Validate JSON serialisability (critical for WebSocket broadcast)
    json_str = json.dumps(result, default=str)
    print(f"[VALIDATE] JSON serialization: OK ({len(json_str)} bytes)")
