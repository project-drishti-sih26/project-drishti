"""
Project Drishti — ML Engine
File: ml_engine/models/ltr_ranker.py
Role: Role 2 — ML/AI Engineer

WHERE Engine Phase 2: Learning-to-Rank using LightGBM LambdaMART.
Ranks candidate ATMs by probability the mule will choose each one.

Phase 1 (now): Stub that raises NotTrainedError if called.
               inference_pipeline.py catches this and falls back to heuristic.
Phase 2 (after Role 5 data is ready): Full LambdaMART training + inference.
"""

import os
import pickle
from typing import List, Dict, Any, Tuple, Optional

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "weights")
MODEL_PATH = os.path.join(WEIGHTS_DIR, "ltr_model.txt")

# ─── Feature column names (in order) ─────────────────────────────────────────
FEATURE_NAMES = [
    "travel_time_mins",
    "distance_km",
    "historical_fraud_count",
    "h3_fraud_density",
    "mule_atm_affinity",
    "mule_network_affinity",
    "time_of_day_sin",
    "time_of_day_cos",
    "is_weekend",
    "bank_match_score",
    "atm_type_encoded",
]

# Module-level model cache
_model = None


class ModelNotTrainedError(Exception):
    """Raised when LambdaMART model weights are not yet available."""
    pass


def _load_model():
    """Lazy-loads the trained LightGBM model from disk."""
    global _model
    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        raise ModelNotTrainedError(
            f"LambdaMART model not found at {MODEL_PATH}. "
            "Run the training notebook first: ml_engine/notebooks/TRAINING_GUIDE.py"
        )

    try:
        import lightgbm as lgb
        _model = lgb.Booster(model_file=MODEL_PATH)
        print(f"[LTRRanker] Loaded trained model from {MODEL_PATH}")
        return _model
    except ImportError:
        raise ModelNotTrainedError("lightgbm not installed. Run: pip install lightgbm")


def _build_feature_vector(
    atm: Dict[str, Any],
    mule_id: str,
    tx_timestamp: str,
) -> List[float]:
    """
    Builds a feature vector for a single (mule, ATM) pair.
    Returns a list of floats in the same order as FEATURE_NAMES.
    """
    import math
    from datetime import datetime

    try:
        from datetime import timezone
        clean_ts = tx_timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_ts)
        # Normalize any timezone-aware datetime strictly to UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        hour = dt.hour
        weekday = dt.weekday()
    except Exception:
        hour = 12
        weekday = 1

    time_sin = math.sin(2 * math.pi * hour / 24)
    time_cos = math.cos(2 * math.pi * hour / 24)
    is_weekend = 1.0 if weekday >= 5 else 0.0

    atm_type_map = {"ATM": 0, "Branch": 1, "Banking_Correspondent": 2}
    atm_type_enc = float(atm_type_map.get(atm.get("location_type", "ATM"), 0))

    return [
        float(atm.get("travel_time_mins", 999)),
        float(atm.get("distance_km", 999)),
        float(atm.get("historical_fraud_count", 0)),
        float(atm.get("h3_fraud_density", 0)),
        float(atm.get("mule_atm_affinity", 0)),
        float(atm.get("mule_network_affinity", 0)),
        time_sin,
        time_cos,
        is_weekend,
        float(atm.get("bank_match_score", 0)),
        atm_type_enc,
    ]


def rank_atm_candidates(
    candidate_atms: List[Dict[str, Any]],
    mule_account_id: str,
    transaction_timestamp: str,
) -> Tuple[List[Dict], Any, List[str], Any]:
    """
    Ranks ATM candidates using the trained LambdaMART model.

    Args:
        candidate_atms:        Candidates from spatial_filter.py
        mule_account_id:       The mule's account ID (for affinity features)
        transaction_timestamp: ISO format timestamp

    Returns:
        Tuple of (ranked_candidates, feature_matrix, feature_names, model)
        ranked_candidates: sorted by score descending
        feature_matrix:    numpy array for SHAP explainability
        feature_names:     list of feature column names
        model:             the loaded LightGBM model object

    Raises:
        ModelNotTrainedError: if model weights don't exist yet.
    """
    import numpy as np

    model = _load_model()  # Raises ModelNotTrainedError if not trained

    # Build feature matrix
    feature_rows = [
        _build_feature_vector(atm, mule_account_id, transaction_timestamp)
        for atm in candidate_atms
    ]
    X = np.array(feature_rows, dtype=float)

    # Predict scores
    scores = model.predict(X)

    # Attach scores to candidates
    ranked = []
    for atm, score in zip(candidate_atms, scores):
        enriched = dict(atm)
        enriched["score"] = round(float(score), 4)
        enriched["confidence_score"] = round(float(score), 4)
        ranked.append(enriched)

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked, X, FEATURE_NAMES, model


def prepare_ltr_training_data(
    historical_tx_path: str,
    atm_data_path: str,
    distance_matrix_path: str,
):
    """
    Prepares the LambdaMART training dataset.
    Run this in ml_engine/notebooks/TRAINING_GUIDE.py (not during inference).

    Returns:
        (X_df, y_labels, groups) ready for lgb.Dataset
    """
    import pandas as pd
    import json

    df = pd.read_csv(historical_tx_path)
    atm_df = pd.read_csv(atm_data_path)
    with open(distance_matrix_path) as f:
        dist_matrix = json.load(f)

    X_rows, y_labels, groups = [], [], []

    # Group by fraud event (each mule transfer is one query)
    grouped = df[df["withdrawal_atm_id"].notna()].groupby("tx_id")

    for tx_id, group in grouped:
        row = group.iloc[0]
        actual_atm = row["withdrawal_atm_id"]
        mule_id = str(row.get("receiver_id") or row.get("mule_account_id") or "ACC_MULE")
        tx_ts = str(row.get("transfer_timestamp", "2026-01-01T12:00:00"))

        # All ATMs in the same city = candidates for this event
        event_candidates = atm_df.to_dict(orient="records")

        for atm in event_candidates:
            features = _build_feature_vector(atm, mule_id, tx_ts)
            label = 3 if atm["location_id"] == actual_atm else 0
            X_rows.append(features)
            y_labels.append(label)

        groups.append(len(event_candidates))

    import numpy as np
    X = pd.DataFrame(X_rows, columns=FEATURE_NAMES)
    y = y_labels
    print(f"[LTRRanker] Training data: {len(y)} rows, {len(groups)} queries")
    return X, y, groups


def train_ltr_model(X, y, groups, save_path: str = MODEL_PATH):
    """
    Trains the LightGBM LambdaMART model.
    Run this from ml_engine/notebooks/TRAINING_GUIDE.py.
    """
    try:
        import lightgbm as lgb
    except ImportError:
        raise ImportError("lightgbm is required. Run: pip install lightgbm")

    train_data = lgb.Dataset(X, label=y, group=groups)

    params = {
        "objective":      "lambdarank",
        "metric":         "ndcg",
        "ndcg_eval_at":   [1, 3, 5],
        "num_leaves":     63,
        "learning_rate":  0.05,
        "feature_fraction": 0.8,
        "verbosity":      -1,
    }

    model = lgb.train(params, train_data, num_boost_round=200)
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    model.save_model(save_path)
    print(f"[LTRRanker] Model saved to {save_path}")
    return model
