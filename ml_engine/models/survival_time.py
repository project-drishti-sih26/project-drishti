"""
Project Drishti — ML Engine
File: ml_engine/models/survival_time.py
Role: Role 2 — ML/AI Engineer

WHEN Engine: Predicts the time window within which the mule runner
will attempt a cash withdrawal, using Survival Analysis.

Phase 1 (Immediate): Smart statistical fallback (no training needed).
Phase 2 (After Role 5's data is ready): Train a real KaplanMeierFitter.
"""

import os
import math
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "weights")
MODEL_PATH = os.path.join(WEIGHTS_DIR, "survival_model.pkl")
HISTORICAL_TX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "simulation", "data", "historical_transactions.csv"
)

# ─── Statistical priors from cybercrime research & SIH blueprint ──────────────
# These are the fallback percentiles when no trained model is available.
# Based on known fraud behavior: most mule cashouts happen within 20-60 min.
_PRIOR_P25_MINS = 22.0   # 25th percentile: earliest likely cashout
_PRIOR_P75_MINS = 47.0   # 75th percentile: latest likely cashout
_PRIOR_CONFIDENCE = 0.58  # Confidence when using prior (lower than trained model)

# ─── Module-level model cache ─────────────────────────────────────────────────
_kmf_model = None


def _load_model() -> Optional[Any]:
    """Lazy-loads the trained KaplanMeierFitter from disk."""
    global _kmf_model
    if _kmf_model is not None:
        return _kmf_model
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                _kmf_model = pickle.load(f)
            print(f"[SurvivalTime] Loaded trained KM model from {MODEL_PATH}")
            return _kmf_model
        except Exception as e:
            print(f"[SurvivalTime] WARNING: Could not load model: {e}")
    return None


def prepare_survival_data(csv_path: str = HISTORICAL_TX_PATH):
    """
    Loads historical_transactions.csv and builds the survival analysis dataset.

    Required CSV columns:
        - mule_account_id
        - transfer_timestamp   (ISO format: "2026-01-15T14:23:00")
        - withdrawal_timestamp (ISO format, or empty if not yet withdrawn)

    Returns:
        pandas DataFrame with columns: ['duration', 'event_occurred']
        duration        = minutes between transfer and withdrawal
        event_occurred  = 1 if withdrawal happened, 0 if censored
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for training. Run: pip install pandas")

    df = pd.read_csv(csv_path)

    df["transfer_ts"] = pd.to_datetime(df["transfer_timestamp"])
    df["withdraw_ts"] = pd.to_datetime(df["withdrawal_timestamp"], errors="coerce")

    df["event_occurred"] = df["withdraw_ts"].notna().astype(int)
    df["duration"] = (df["withdraw_ts"] - df["transfer_ts"]).dt.total_seconds() / 60

    # For censored events, use a reasonable upper bound duration
    max_observed = df.loc[df["event_occurred"] == 1, "duration"].max()
    df["duration"] = df["duration"].fillna(max_observed if not math.isnan(max_observed) else 120)
    df = df[df["duration"] > 0]  # Remove zero/negative durations

    print(f"[SurvivalTime] Prepared {len(df)} records | "
          f"Events: {df['event_occurred'].sum()} | Censored: {(df['event_occurred'] == 0).sum()}")
    return df[["duration", "event_occurred"]]


def train_survival_model(df, save: bool = True):
    """
    Fits a KaplanMeierFitter on the prepared survival dataset.

    Args:
        df: DataFrame with 'duration' and 'event_occurred' columns.
        save: If True, saves the fitted model to ml_engine/weights/.

    Returns:
        Fitted KaplanMeierFitter object.
    """
    try:
        from lifelines import KaplanMeierFitter
    except ImportError:
        raise ImportError("lifelines is required. Run: pip install lifelines")

    kmf = KaplanMeierFitter()
    kmf.fit(
        durations=df["duration"],
        event_observed=df["event_occurred"],
        label="Mule Withdrawal Time (mins)",
    )

    if save:
        os.makedirs(WEIGHTS_DIR, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(kmf, f)
        print(f"[SurvivalTime] Model saved to {MODEL_PATH}")

    # Print key percentile summary
    median = kmf.median_survival_time_
    print(f"[SurvivalTime] Trained. Median cashout time: {median:.1f} minutes")
    return kmf


def _extract_percentile_from_kmf(kmf, percentile: float) -> float:
    """
    Extracts the time (in minutes) at which the survival function
    crosses a given survival probability level.

    For example, percentile=0.25 finds T where S(T) = 0.75
    (meaning 25% of mules have already withdrawn by time T).

    Args:
        kmf: Fitted KaplanMeierFitter.
        percentile: Float between 0 and 1 (e.g., 0.25 for 25th percentile).
    Returns:
        Time in minutes (float).
    """
    import numpy as np
    sf = kmf.survival_function_
    times = sf.index.values
    probs = sf.iloc[:, 0].values  # S(t) values

    target_survival = 1.0 - percentile  # S(t) = 1 - CDF
    # Find the first time where S(t) drops to or below target
    candidates = times[probs <= target_survival]
    if len(candidates) == 0:
        return float(times[-1])  # Return last observed time if never reached
    return float(candidates[0])


def predict_time_window(
    transaction_timestamp: str,
    mule_account_id: str = "",
    low_percentile: float = 0.25,
    high_percentile: float = 0.75,
) -> Dict[str, Any]:
    """
    Predicts the cashout time window for a mule transaction.

    Args:
        transaction_timestamp: ISO format string of when the transfer occurred.
        mule_account_id: The mule's account ID (for future per-mule models).
        low_percentile:  Lower bound of the prediction interval (default 25%).
        high_percentile: Upper bound of the prediction interval (default 75%).

    Returns:
        dict with keys: start, end, minutes_from_now, confidence
    """
    try:
        tx_dt = datetime.fromisoformat(transaction_timestamp.replace("Z", "+00:00"))
    except Exception:
        tx_dt = datetime.utcnow()

    now = datetime.utcnow()

    # ── Try trained model ──────────────────────────────────────────────────
    model = _load_model()
    if model is not None:
        try:
            t_low  = _extract_percentile_from_kmf(model, low_percentile)
            t_high = _extract_percentile_from_kmf(model, high_percentile)
            confidence = round(high_percentile - low_percentile + 0.2, 2)
            print(f"[SurvivalTime] Model prediction: window = {t_low:.0f} – {t_high:.0f} mins")
        except Exception as e:
            print(f"[SurvivalTime] Model prediction failed: {e}. Using statistical prior.")
            t_low, t_high, confidence = _PRIOR_P25_MINS, _PRIOR_P75_MINS, _PRIOR_CONFIDENCE
    else:
        # ── Fallback: Statistical prior from cybercrime research ──────────
        print("[SurvivalTime] No trained model. Using statistical prior window.")
        t_low, t_high, confidence = _PRIOR_P25_MINS, _PRIOR_P75_MINS, _PRIOR_CONFIDENCE

    window_start = tx_dt + timedelta(minutes=t_low)
    window_end   = tx_dt + timedelta(minutes=t_high)

    # Time remaining from NOW until window starts (urgency for police)
    minutes_from_now = max(0, int((window_start - now).total_seconds() / 60))

    return {
        "start": window_start.strftime("%Y-%m-%dT%H:%M:%S"),
        "end": window_end.strftime("%Y-%m-%dT%H:%M:%S"),
        "minutes_from_now": minutes_from_now,
        "confidence": confidence,
        "model_source": "KaplanMeier" if model else "StatisticalPrior",
    }


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from datetime import timezone

    tx_time = datetime.utcnow().isoformat()
    print(f"\n[TEST] Transaction timestamp: {tx_time}")

    result = predict_time_window(
        transaction_timestamp=tx_time,
        mule_account_id="ACC_MULE_0042",
    )

    print(f"\n[RESULTS] Predicted Cashout Window:")
    print(f"  Window Start     : {result['start']}")
    print(f"  Window End       : {result['end']}")
    print(f"  Minutes From Now : {result['minutes_from_now']} min")
    print(f"  Confidence       : {result['confidence']}")
    print(f"  Model Source     : {result['model_source']}")
    print(f"\n  --> Police have ~{result['minutes_from_now']} minutes to intercept!")
