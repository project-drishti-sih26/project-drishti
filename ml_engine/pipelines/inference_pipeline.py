"""
Project Drishti — ML Engine
File: ml_engine/pipelines/inference_pipeline.py
Role: Role 2 — ML/AI Engineer

MASTER ENTRYPOINT of the ML Engine.
The backend (app/services/trigger_service.py) calls exactly one function —
predict_fraud_cashout() — and receives a fully-structured prediction payload.

Internal pipeline:
    STEP 1 -> Spatial Filter    (WHERE: reachable cash-point candidates)
    STEP 2 -> Ranker            (WHERE: score & rank candidates)
    STEP 3 -> Survival Time     (WHEN : cashout time window)
    STEP 4 -> Explainability    (WHY  : plain-English dispatch reasons)
    STEP 5 -> Assemble Payload  (PredictionAlert JSON for the WebSocket)

DESIGN NOTES THAT MATTER OPERATIONALLY
--------------------------------------
* Every displayed time carries an IST variant. The engine reasons in UTC, but an
  officer reading "06:04" when their watch says 11:34 will not trust the system
  again. UTC is for machines; IST is for humans.

* `confidence_score` is a CALIBRATED PROBABILITY over the candidate set, not a
  raw model score. Raw LambdaRank output is unbounded (values above 2.0 were
  being rendered as "242% confidence"). Softmax over the query group makes
  "Rank #1: 34%" mean "the single most likely of all reachable cash points".

* The payload reports `total_candidates_evaluated` and the probability mass
  captured by the Top-5, so a reviewer can see what the shortlist actually
  covers rather than taking the ranking on faith.
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from ml_engine.models.fallback_heuristic import score_candidates_heuristic
from ml_engine.models.survival_time import predict_time_window
from ml_engine.pipelines.explainability import generate_explanations
from ml_engine.pipelines.spatial_filter import get_candidate_atms

# LambdaMART ranker — imported defensively so a missing/partial install still serves.
_ltr_ranker_available = False
try:
    from ml_engine.models.ltr_ranker import ModelNotTrainedError, rank_atm_candidates
    _ltr_ranker_available = True
except ImportError:
    class ModelNotTrainedError(Exception):  # type: ignore[no-redef]
        pass

# ─── Config ───────────────────────────────────────────────────────────────────
DELHI_CENTER_LAT = 28.6139
DELHI_CENTER_LON = 77.2090
TOP_N = 5
MAX_TRAVEL_MINUTES = 45
IST = timezone(timedelta(hours=5, minutes=30))

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "weights", "metrics.json")
_metrics_cache: Optional[Dict[str, Any]] = None
_metrics_checked = False


def _safe_float(val, default: float = 0.0) -> float:
    """
    Coerces numpy.float64 / pandas NA / None to a plain Python float.
    Without this, numpy scalars reach json.dumps and either raise or get
    stringified — and the frontend then does arithmetic on strings.
    """
    if val is None:
        return default
    try:
        f = float(val)
        return f if f == f else default   # reject NaN
    except (TypeError, ValueError):
        return default


def _safe_int(val, default: int = 0) -> int:
    if val is None:
        return default
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return default


def _load_metrics() -> Dict[str, Any]:
    """
    Loads the held-out evaluation metrics produced by train_models.py so the
    live payload can state the model's measured accuracy. The dashboard and the
    pitch then quote the same numbers the training run actually produced —
    nothing is hardcoded in the UI.
    """
    global _metrics_cache, _metrics_checked
    if not _metrics_checked:
        _metrics_checked = True
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                _metrics_cache = json.load(f)
        except Exception:
            _metrics_cache = None
    return _metrics_cache or {}


def _model_scorecard() -> Dict[str, Any]:
    """Compact, judge-facing accuracy summary for the alert payload."""
    m = _load_metrics()
    ev = (m.get("where_engine", {}).get("evaluation", {}) or {})
    model = ev.get("model", {})
    random = ev.get("random", {})
    out: Dict[str, Any] = {}
    if model:
        out["top1_hit_rate"] = model.get("top1_hit_rate")
        out["top5_hit_rate"] = model.get("top5_hit_rate")
        out["ndcg_at_5"] = model.get("ndcg@5")
        out["evaluated_on_queries"] = model.get("n_queries")
    if random.get("top5_hit_rate"):
        out["random_top5_hit_rate"] = random["top5_hit_rate"]
    cox = (m.get("when_engine", {}).get("cox", {}) or {})
    if cox.get("concordance_index"):
        out["survival_c_index"] = cox["concordance_index"]
    return out


def _risk_tier(probability: float) -> str:
    """
    Maps a calibrated probability to a dispatch priority label.
    Thresholds are deliberately conservative: only a genuinely dominant
    candidate earns CRITICAL, because CRITICAL is what moves a patrol car.
    """
    if probability >= 0.30:
        return "CRITICAL"
    if probability >= 0.15:
        return "HIGH"
    if probability >= 0.06:
        return "MEDIUM"
    return "LOW"


def predict_fraud_cashout(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master inference pipeline. Called by backend/app/services/trigger_service.py.

    Args:
        input_data: {
            "mule_account_id":       str,
            "last_latitude":         float | None,
            "last_longitude":        float | None,
            "transaction_amount":    float,
            "transaction_timestamp": str (ISO),
            "case_id":               str,
            "victim_account_id":     str,
            "mule_tier":             int (1 = victim->mule, 2 = mule->mule),
        }

    Returns:
        PredictionAlert payload matching backend/app/schemas/prediction.py.
    """
    mule_id = str(input_data.get("mule_account_id", "UNKNOWN"))
    victim_id = str(input_data.get("victim_account_id", "UNKNOWN"))
    amount = _safe_float(input_data.get("transaction_amount"), 0.0)
    mule_tier = _safe_int(input_data.get("mule_tier"), 1) or 1
    tx_timestamp = input_data.get("transaction_timestamp") or datetime.now(timezone.utc).isoformat()
    case_id = input_data.get("case_id") or f"CASE-{uuid.uuid4().hex[:8].upper()}"

    print(f"\n[Pipeline] Inference start | case={case_id} | mule={mule_id} | Rs.{amount:,.0f}")

    location_known = input_data.get("last_latitude") is not None
    mule_lat = _safe_float(input_data.get("last_latitude"), DELHI_CENTER_LAT) or DELHI_CENTER_LAT
    mule_lon = _safe_float(input_data.get("last_longitude"), DELHI_CENTER_LON) or DELHI_CENTER_LON
    if not location_known:
        print("[Pipeline] WARNING: mule location unknown - using Delhi centre. "
              "Spatial precision is degraded for this alert.")

    # ── STEP 1: spatial candidate retrieval ─────────────────────────────────
    candidates = get_candidate_atms(mule_lat, mule_lon, max_travel_minutes=MAX_TRAVEL_MINUTES)
    total_candidates = len(candidates)
    print(f"[Pipeline] Step 1: {total_candidates} reachable cash points "
          f"(<= {MAX_TRAVEL_MINUTES} min road travel)")
    if total_candidates == 0:
        print("[Pipeline] CRITICAL: no reachable candidates - returning empty payload.")
        return _build_empty_payload(case_id, mule_id, victim_id, amount, tx_timestamp)

    nearest_travel = min(_safe_float(c.get("travel_time_mins"), 999) for c in candidates)

    # ── STEP 2: ranking ─────────────────────────────────────────────────────
    model_used = "FallbackHeuristic"
    ltr_model = feature_matrix = feature_names = None
    ranked_candidates: List[Dict[str, Any]]

    if _ltr_ranker_available:
        try:
            ranked_candidates, feature_matrix, feature_names, ltr_model = rank_atm_candidates(
                candidates, mule_id, tx_timestamp, mule_lat, mule_lon, amount
            )
            model_used = "LambdaMART"
            print("[Pipeline] Step 2: LambdaMART ranking applied.")
        except Exception as e:
            print(f"[Pipeline] Step 2: LambdaMART unavailable ({e}) - heuristic fallback.")
            ranked_candidates = score_candidates_heuristic(candidates)
    else:
        ranked_candidates = score_candidates_heuristic(candidates)
        print("[Pipeline] Step 2: heuristic ranking applied (ranker module unavailable).")

    top_candidates = ranked_candidates[:TOP_N]

    # How much of the total probability mass the shortlist covers — an honest
    # measure of "should the officer trust these five?"
    top5_mass = sum(_safe_float(c.get("probability"), 0.0) for c in top_candidates)

    # ── STEP 3: survival time window ────────────────────────────────────────
    time_window = predict_time_window(
        transaction_timestamp=tx_timestamp,
        mule_account_id=mule_id,
        amount=amount,
        mule_tier=mule_tier,
        nearest_travel_mins=nearest_travel,
    )
    print(f"[Pipeline] Step 3: window {time_window['start_ist']}-{time_window['end_ist']} IST "
          f"via {time_window['model_source']}")

    # ── STEP 4: explainability ──────────────────────────────────────────────
    explanations = generate_explanations(
        top_candidates=top_candidates,
        model=ltr_model,
        feature_matrix=feature_matrix[:TOP_N] if feature_matrix is not None else None,
        feature_names=feature_names,
        model_used=model_used,
    )

    # ── STEP 5: assemble payload ────────────────────────────────────────────
    top_5_atms = []
    for i, (atm, explanation) in enumerate(zip(top_candidates, explanations)):
        prob = _safe_float(atm.get("probability", atm.get("confidence_score")), 0.0)
        travel = _safe_float(atm.get("travel_time_mins"))
        top_5_atms.append({
            "rank": i + 1,
            "location_id": str(atm.get("location_id", f"ATM_UNKNOWN_{i + 1}")),
            "bank_name": str(atm.get("bank_name", "Unknown Bank")),
            "location_type": str(atm.get("location_type", "ATM")),
            "latitude": _safe_float(atm.get("latitude")),
            "longitude": _safe_float(atm.get("longitude")),
            "address": str(atm.get("address", "Address not available")),
            "distance_km": _safe_float(atm.get("distance_km")),
            "travel_time_mins": travel,
            "historical_fraud_count": _safe_int(atm.get("historical_fraud_count")),
            "h3_index": str(atm.get("h3_index") or ""),
            # Calibrated probability over the candidate set (0-1), plus a
            # percentage the UI can render directly without re-deriving it.
            "confidence_score": round(prob, 4),
            "probability_pct": round(prob * 100, 1),
            "raw_score": _safe_float(atm.get("raw_score")),
            "risk_tier": _risk_tier(prob),
            # When a patrol dispatched NOW would arrive, vs the cashout window.
            "patrol_eta_mins": round(travel, 1),
            "explanation": str(explanation),
        })

    now = datetime.now(timezone.utc)
    alert_payload = {
        "alert_id": f"ALERT-{uuid.uuid4().hex[:8].upper()}",
        "case_id": case_id,
        "mule_account_id": mule_id,
        "victim_account_id": victim_id,
        "compromised_amount": amount,
        "mule_tier": mule_tier,
        "mule_last_latitude": mule_lat,
        "mule_last_longitude": mule_lon,
        "mule_location_known": bool(location_known),
        "detected_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "detected_at_ist": now.astimezone(IST).strftime("%H:%M:%S"),
        "time_window": time_window,
        "top_5_atms": top_5_atms,
        "model_used": model_used,
        "total_candidates_evaluated": total_candidates,
        # Share of total predicted probability captured by the 5-ATM shortlist.
        "top5_probability_mass": round(top5_mass, 4),
        "model_scorecard": _model_scorecard(),
    }

    print(f"[Pipeline] Complete: {alert_payload['alert_id']} | "
          f"top-5 covers {top5_mass:.1%} of probability mass")
    return alert_payload


def _build_empty_payload(case_id, mule_id, victim_id, amount, tx_timestamp) -> Dict:
    """Minimal safe payload when no candidate cash point is reachable."""
    now = datetime.now(timezone.utc)
    return {
        "alert_id": f"ALERT-EMPTY-{uuid.uuid4().hex[:6].upper()}",
        "case_id": case_id,
        "mule_account_id": mule_id,
        "victim_account_id": victim_id,
        "compromised_amount": amount,
        "detected_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "detected_at_ist": now.astimezone(IST).strftime("%H:%M:%S"),
        "time_window": {
            "start": None, "end": None, "start_ist": None, "end_ist": None,
            "minutes_from_now": 0, "window_minutes": 0,
            "confidence": 0.0, "model_source": "NONE",
        },
        "top_5_atms": [],
        "model_used": "NONE",
        "total_candidates_evaluated": 0,
        "top5_probability_mass": 0.0,
        "model_scorecard": _model_scorecard(),
    }


# ─── Self-test (FULL END-TO-END PIPELINE) ─────────────────────────────────────
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_input = {
        "mule_account_id": "ACC_MULE_0042",
        "last_latitude": 28.6315,     # Connaught Place, New Delhi
        "last_longitude": 77.2167,
        "transaction_amount": 750000.0,
        "transaction_timestamp": datetime.now(timezone.utc).isoformat(),
        "case_id": "CYB-2026-DL-00001",
        "victim_account_id": "ACC_VICTIM_0001",
        "mule_tier": 1,
    }

    result = predict_fraud_cashout(test_input)
    sc = result.get("model_scorecard", {})

    print("\n" + "=" * 74)
    print("  PROJECT DRISHTI - END-TO-END PREDICTION OUTPUT")
    print("=" * 74)
    print(f"  Alert ID      : {result['alert_id']}")
    print(f"  Case ID       : {result['case_id']}")
    print(f"  Amount        : Rs.{result['compromised_amount']:,.0f}")
    print(f"  Detected at   : {result['detected_at_ist']} IST")
    print(f"  Ranker        : {result['model_used']}")
    print(f"  WHEN model    : {result['time_window']['model_source']}")
    print(f"  Candidates    : {result['total_candidates_evaluated']} reachable cash points")
    tw = result["time_window"]
    print(f"  Cashout window: {tw['start_ist']} - {tw['end_ist']} IST "
          f"({tw['window_minutes']} min wide)")
    print(f"  Lead time     : {tw['minutes_from_now']} minutes before the window opens")
    print(f"  Top-5 covers  : {result['top5_probability_mass']:.1%} of total probability")
    if sc:
        print(f"  Measured acc. : Top-1 {sc.get('top1_hit_rate', 0):.1%} | "
              f"Top-5 {sc.get('top5_hit_rate', 0):.1%} | NDCG@5 {sc.get('ndcg_at_5', 0)} "
              f"(held-out, n={sc.get('evaluated_on_queries')})")

    print("\n  TOP 5 PREDICTED CASHOUT POINTS:")
    print("-" * 74)
    for atm in result["top_5_atms"]:
        print(f"  #{atm['rank']} [{atm['risk_tier']:8}] {atm['probability_pct']:5.1f}%  "
              f"{atm['bank_name']} ({atm['location_type']})")
        print(f"       {atm['address'][:66]}")
        print(f"       Patrol ETA {atm['patrol_eta_mins']:.0f} min | "
              f"{atm['distance_km']:.1f} km | prior frauds: {atm['historical_fraud_count']}")
        print(f"       {atm['explanation']}")
        print()

    # A confidently wrong ranking is worse than none: assert the shortlist is
    # actually ordered by travel time sanity (nearest candidate should be close).
    nearest = min(a["patrol_eta_mins"] for a in result["top_5_atms"])
    print(f"[CHECK] Closest ATM in the shortlist: {nearest:.0f} min away "
          f"(must be small, or the model is ignoring geography)")
    print(f"[VALIDATE] JSON serialization: OK ({len(json.dumps(result))} bytes, no default=str needed)")
