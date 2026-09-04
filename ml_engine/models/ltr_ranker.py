"""
Project Drishti — ML Engine
File: ml_engine/models/ltr_ranker.py
Role: Role 2 — ML/AI Engineer

WHERE Engine Phase 2: Learning-to-Rank with LightGBM LambdaMART.
Ranks candidate ATMs by the probability the mule runner will choose each one.

WHY LEARNING-TO-RANK AND NOT CLASSIFICATION
-------------------------------------------
A binary classifier asks "will a cashout happen at this ATM?" — but ~99.4% of
candidates are negatives, so the loss is dominated by an easy majority class and
the model optimises for the wrong thing. Police do not need a probability per
ATM; they need a *correctly ordered shortlist* to allocate a limited number of
patrol units to. LambdaMART optimises NDCG directly — i.e. it optimises the
ordering itself — which is precisely the operational objective.

CALIBRATION
-----------
Raw LambdaRank scores are unbounded (we observed +2.42). Showing that to an
officer as "confidence 242%" destroys trust. `_softmax` converts the scores
within a query group into a proper probability distribution over the candidate
set that sums to 1.0, so "Rank #1: 34%" means "of all reachable ATMs, this one
is the single most likely, at 34%".
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from ml_engine.features.feature_store import (
    FEATURE_NAMES,
    build_feature_matrix,
    get_store,
)

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "weights")
MODEL_PATH = os.path.join(WEIGHTS_DIR, "ltr_model.txt")
CALIBRATION_PATH = os.path.join(WEIGHTS_DIR, "calibration.json")

# Module-level model cache
_model = None
_model_load_failed = False
_temperature: Optional[float] = None


def _load_temperature() -> float:
    """
    Loads the softmax temperature fitted by train_models.py on held-out
    validation queries. Falls back to 1.0 (plain softmax) if absent.
    """
    global _temperature
    if _temperature is None:
        _temperature = 1.0
        try:
            with open(CALIBRATION_PATH, "r", encoding="utf-8") as f:
                t = float(json.load(f).get("temperature", 1.0))
            if t > 0:
                _temperature = t
                print(f"[LTRRanker] Using fitted calibration temperature T={t}")
        except Exception:
            print("[LTRRanker] No calibration file - using uncalibrated softmax (T=1.0).")
    return _temperature


class ModelNotTrainedError(Exception):
    """Raised when LambdaMART model weights are not yet available."""
    pass


def _load_model():
    """Lazy-loads the trained LightGBM model from disk."""
    global _model, _model_load_failed
    if _model is not None:
        return _model
    if _model_load_failed:
        raise ModelNotTrainedError("LambdaMART model previously failed to load.")

    if not os.path.exists(MODEL_PATH):
        _model_load_failed = True
        raise ModelNotTrainedError(
            f"LambdaMART model not found at {MODEL_PATH}. "
            "Train it first: python ml_engine/train_models.py"
        )
    try:
        import lightgbm as lgb
        _model = lgb.Booster(model_file=MODEL_PATH)
    except ImportError:
        _model_load_failed = True
        raise ModelNotTrainedError("lightgbm not installed. Run: pip install lightgbm")

    # ── Guard against the exact bug that shipped before ────────────────────
    # If the model has no splits on travel time, it is not a spatial model and
    # will send patrols to the wrong ATM. Refuse to serve it; the heuristic
    # fallback is strictly better than a confidently wrong ranking.
    try:
        names = _model.feature_name()
        imp = _model.feature_importance(importance_type="split")
        by_name = dict(zip(names, imp))
        travel_splits = by_name.get("travel_time_mins", 0) + by_name.get("distance_km", 0)
        if travel_splits == 0:
            _model = None
            _model_load_failed = True
            raise ModelNotTrainedError(
                "Loaded LambdaMART model has 0 splits on travel_time_mins/distance_km "
                "— it ignores geography and would misdirect patrols. "
                "Retrain with: python ml_engine/train_models.py"
            )
    except ModelNotTrainedError:
        raise
    except Exception:
        pass  # importance introspection is best-effort only

    print(f"[LTRRanker] Loaded trained model from {MODEL_PATH}")
    return _model


def _softmax(scores, temperature: float = 1.0) -> List[float]:
    """
    Numerically stable temperature-scaled softmax over a query group's raw scores.

    `temperature` is fitted on held-out data (see train_models.fit_temperature).
    It does not change the ordering — only the reported probabilities — so a
    bad calibration file can never degrade ranking quality.
    """
    import numpy as np
    s = np.asarray(scores, dtype=float) / max(temperature, 1e-6)
    s = s - s.max()
    e = np.exp(s)
    total = e.sum()
    if total <= 0 or not np.isfinite(total):
        return [1.0 / len(s)] * len(s)
    return (e / total).tolist()


def rank_atm_candidates(
    candidate_atms: List[Dict[str, Any]],
    mule_account_id: str,
    transaction_timestamp: str,
    mule_lat: float,
    mule_lon: float,
    amount: float = 0.0,
) -> Tuple[List[Dict], Any, List[str], Any]:
    """
    Ranks ATM candidates using the trained LambdaMART model.

    Args:
        candidate_atms:        Candidates from spatial_filter.get_candidate_atms()
                               (must already carry travel_time_mins / distance_km).
        mule_account_id:       Mule's account ID (drives the affinity feature).
        transaction_timestamp: ISO timestamp of the incoming transfer.
        mule_lat, mule_lon:    Mule's last known position.
        amount:                Compromised amount in ₹.

    Returns:
        (ranked_candidates, feature_matrix, feature_names, model)
        ranked_candidates carry:
            raw_score        — unbounded LambdaRank score (for debugging)
            probability      — calibrated softmax probability over the candidate set
            confidence_score — alias of probability, consumed by the frontend

    Raises:
        ModelNotTrainedError: if usable model weights don't exist.
    """
    model = _load_model()  # raises if untrained / non-spatial

    store = get_store()
    X = build_feature_matrix(
        candidate_atms, mule_account_id, transaction_timestamp,
        mule_lat, mule_lon, amount, store,
    )

    raw_scores = model.predict(X)
    probabilities = _softmax(raw_scores, _load_temperature())

    ranked = []
    for atm, raw, prob in zip(candidate_atms, raw_scores, probabilities):
        enriched = dict(atm)
        enriched["raw_score"] = round(float(raw), 4)
        enriched["probability"] = round(float(prob), 6)
        enriched["confidence_score"] = round(float(prob), 6)
        enriched["score"] = round(float(prob), 6)
        ranked.append(enriched)

    # Sort by raw score (identical ordering to probability, but avoids ties from
    # float rounding at 6 dp when many candidates have near-zero probability).
    order = sorted(range(len(ranked)), key=lambda i: raw_scores[i], reverse=True)
    ranked = [ranked[i] for i in order]
    X_sorted = X[order]

    return ranked, X_sorted, FEATURE_NAMES, model


def get_feature_importance() -> Optional[List[Tuple[str, int]]]:
    """
    Returns [(feature_name, n_splits), ...] sorted descending.
    Useful for the judge-facing "what is the model actually using?" slide.
    """
    try:
        model = _load_model()
    except ModelNotTrainedError:
        return None
    pairs = list(zip(model.feature_name(), model.feature_importance(importance_type="split")))
    return sorted(pairs, key=lambda x: -x[1])


if __name__ == "__main__":
    imp = get_feature_importance()
    if imp is None:
        print("No trained model. Run: python ml_engine/train_models.py")
    else:
        print("\nLambdaMART feature importance (tree splits):")
        for name, n in imp:
            bar = "#" * int(40 * n / max(imp[0][1], 1))
            print(f"  {name:26} {n:6}  {bar}")
