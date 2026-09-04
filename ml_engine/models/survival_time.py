"""
Project Drishti — ML Engine
File: ml_engine/models/survival_time.py
Role: Role 2 — ML/AI Engineer

WHEN Engine: predicts the time window in which the mule runner will attempt a
cash withdrawal, using Survival Analysis on right-censored data.

WHY SURVIVAL ANALYSIS AND NOT PLAIN REGRESSION
----------------------------------------------
Roughly 18% of flagged fraud transfers never produce an observed withdrawal —
the account gets frozen, or the runner aborts. Those rows are *right-censored*:
we know the cashout hadn't happened by the time we stopped watching, not that it
never would. Dropping them biases every estimate toward fast cashouts; imputing
a fake duration for them biases it the other way. Survival analysis is the only
formulation that uses censored rows correctly, and it natively outputs an
interval rather than a single number — which is what a dispatch window is.

THREE-TIER PREDICTION LADDER (each tier degrades gracefully)
------------------------------------------------------------
  Tier 1  Cox Proportional Hazards  — window conditioned on THIS case's
          covariates (amount, IST hour, mule tier, distance to nearest cash
          point). Different cases get different windows.
  Tier 2  Kaplan-Meier              — population-level window. Same for every
          case, but empirically grounded in the observed data.
  Tier 3  Statistical prior         — hardcoded research-based percentiles, so
          the system still answers on a fresh clone with no trained weights.

Tier 2 alone was the previous behaviour and it is worth being explicit about the
weakness: a Kaplan-Meier fitter takes no inputs, so it returns an identical
window for a ₹50,001 daytime transfer and a ₹25 lakh 3 a.m. transfer. That is a
constant presented as a prediction. Cox PH fixes it.
"""

import os
import pickle
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "weights")
KM_MODEL_PATH = os.path.join(WEIGHTS_DIR, "survival_model.pkl")
COX_MODEL_PATH = os.path.join(WEIGHTS_DIR, "cox_model.pkl")
HISTORICAL_TX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "simulation", "data", "historical_transactions.csv"
)

IST = timezone(timedelta(hours=5, minutes=30))

# ─── Tier-3 statistical priors (cybercrime research + blueprint) ──────────────
_PRIOR_P25_MINS = 22.0
_PRIOR_P75_MINS = 47.0
_PRIOR_CONFIDENCE = 0.55

# ─── Module-level caches ──────────────────────────────────────────────────────
_kmf_model = None
_cox_model = None
_km_checked = False
_cox_checked = False


def _load_km():
    global _kmf_model, _km_checked
    if _kmf_model is None and not _km_checked:
        _km_checked = True
        if os.path.exists(KM_MODEL_PATH):
            try:
                with open(KM_MODEL_PATH, "rb") as f:
                    _kmf_model = pickle.load(f)
                print(f"[SurvivalTime] Loaded Kaplan-Meier model from {KM_MODEL_PATH}")
            except Exception as e:
                print(f"[SurvivalTime] WARNING: Kaplan-Meier load failed: {e}")
    return _kmf_model


def _load_cox():
    global _cox_model, _cox_checked
    if _cox_model is None and not _cox_checked:
        _cox_checked = True
        if os.path.exists(COX_MODEL_PATH):
            try:
                with open(COX_MODEL_PATH, "rb") as f:
                    _cox_model = pickle.load(f)
                print(f"[SurvivalTime] Loaded Cox PH model from {COX_MODEL_PATH}")
            except Exception as e:
                print(f"[SurvivalTime] WARNING: Cox PH load failed: {e}")
    return _cox_model


def _parse_ts(ts: Any) -> datetime:
    """Parses an ISO-ish timestamp into a tz-aware UTC datetime."""
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _percentile_from_km(kmf, p: float) -> float:
    """Time at which the survival function crosses S(t) = 1 - p."""
    try:
        val = float(kmf.percentile(1.0 - p))
        if val == val and val > 0:  # not NaN
            return val
    except Exception:
        pass
    sf = kmf.survival_function_
    times, probs = sf.index.values, sf.iloc[:, 0].values
    hit = times[probs <= (1.0 - p)]
    return float(hit[0]) if len(hit) else float(times[-1])


def _percentiles_from_cox(cph, covariates: Dict[str, float], low: float, high: float):
    """
    Per-case percentiles from the Cox PH partial-hazard survival curve.
    Returns (t_low, t_high) in minutes, or None if the model can't score this row.
    """
    import pandas as pd

    needed = list(getattr(cph, "params_", pd.Series(dtype=float)).index)
    if not needed:
        return None
    row = pd.DataFrame([{k: float(covariates.get(k, 0.0)) for k in needed}])
    sf = cph.predict_survival_function(row)
    times = sf.index.values
    probs = sf.iloc[:, 0].values

    def cross(p: float) -> float:
        hit = times[probs <= (1.0 - p)]
        return float(hit[0]) if len(hit) else float(times[-1])

    return cross(low), cross(high)


def predict_time_window(
    transaction_timestamp: str,
    mule_account_id: str = "",
    low_percentile: float = 0.25,
    high_percentile: float = 0.75,
    amount: float = 0.0,
    mule_tier: int = 1,
    nearest_travel_mins: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Predicts the cashout window for one mule transaction.

    Args:
        transaction_timestamp: ISO timestamp of the incoming transfer.
        mule_account_id:       Mule account ID (reserved for per-mule models).
        low_percentile:        Lower bound of the interval (default 25%).
        high_percentile:       Upper bound of the interval (default 75%).
        amount:                Compromised amount in ₹ (Cox covariate).
        mule_tier:             1 = direct from victim, 2 = mule-to-mule hop.
        nearest_travel_mins:   Road minutes to the closest reachable cash point.

    Returns:
        {start, end, start_ist, end_ist, minutes_from_now, window_minutes,
         confidence, model_source}
        `start`/`end` are UTC ISO strings (machine-facing).
        `start_ist`/`end_ist` are 24-hour IST strings (officer-facing).
    """
    tx_dt = _parse_ts(transaction_timestamp)
    now = datetime.now(timezone.utc)

    ist_hour = tx_dt.astimezone(IST).hour
    t_low = t_high = None
    source = "StatisticalPrior"
    confidence = _PRIOR_CONFIDENCE

    # ── Tier 1: Cox PH (case-specific) ───────────────────────────────────────
    cph = _load_cox()
    if cph is not None:
        try:
            covariates = {
                "amount_lakhs": amount / 100000.0,
                "ist_hour": float(ist_hour),
                "is_night": 1.0 if (ist_hour >= 22 or ist_hour < 5) else 0.0,
                "mule_tier": float(mule_tier),
                "travel_mins": float(nearest_travel_mins) if nearest_travel_mins is not None else 8.0,
            }
            res = _percentiles_from_cox(cph, covariates, low_percentile, high_percentile)
            if res and res[1] > res[0] > 0:
                t_low, t_high = res
                source = "CoxProportionalHazards"
                # Cox uses case covariates, so we credit it slightly higher
                # confidence than the population-level KM curve.
                confidence = round(min(0.92, high_percentile - low_percentile + 0.35), 2)
                print(f"[SurvivalTime] Cox PH window: {t_low:.0f}-{t_high:.0f} min "
                      f"(amount=₹{amount:,.0f}, IST hour={ist_hour}, tier={mule_tier})")
        except Exception as e:
            print(f"[SurvivalTime] Cox PH prediction failed ({e}) - falling back to Kaplan-Meier.")

    # ── Tier 2: Kaplan-Meier (population) ────────────────────────────────────
    if t_low is None:
        kmf = _load_km()
        if kmf is not None:
            try:
                t_low = _percentile_from_km(kmf, low_percentile)
                t_high = _percentile_from_km(kmf, high_percentile)
                source = "KaplanMeier"
                confidence = round(high_percentile - low_percentile + 0.2, 2)
                print(f"[SurvivalTime] Kaplan-Meier window: {t_low:.0f}-{t_high:.0f} min")
            except Exception as e:
                print(f"[SurvivalTime] Kaplan-Meier prediction failed ({e}).")

    # ── Tier 3: statistical prior ────────────────────────────────────────────
    if t_low is None or t_high is None or not (t_high > t_low > 0):
        t_low, t_high = _PRIOR_P25_MINS, _PRIOR_P75_MINS
        source = "StatisticalPrior"
        confidence = _PRIOR_CONFIDENCE
        print("[SurvivalTime] Using statistical prior window (no usable trained model).")

    window_start = tx_dt + timedelta(minutes=t_low)
    window_end = tx_dt + timedelta(minutes=t_high)

    return {
        "start": window_start.strftime("%Y-%m-%dT%H:%M:%S"),
        "end": window_end.strftime("%Y-%m-%dT%H:%M:%S"),
        "start_ist": window_start.astimezone(IST).strftime("%H:%M"),
        "end_ist": window_end.astimezone(IST).strftime("%H:%M"),
        "minutes_from_now": max(0, int((window_start - now).total_seconds() / 60)),
        "window_minutes": int(round(t_high - t_low)),
        "confidence": confidence,
        "model_source": source,
    }


# ─── Training helpers (kept for the notebook / retraining path) ────────────────
def prepare_survival_data(csv_path: str = HISTORICAL_TX_PATH):
    """
    Builds the survival dataset from historical_transactions.csv.

    Returns a DataFrame with ['duration', 'event_occurred'].
    Censored rows get duration = transfer -> study end (now), which is the only
    statistically valid choice; a constant would bias the KM curve.
    """
    import pandas as pd

    df = pd.read_csv(csv_path)
    df["transfer_ts"] = pd.to_datetime(df["transfer_timestamp"], errors="coerce")
    df["withdraw_ts"] = pd.to_datetime(df["withdrawal_timestamp"], errors="coerce")
    df["event_occurred"] = df["withdraw_ts"].notna().astype(int)
    df["duration"] = (df["withdraw_ts"] - df["transfer_ts"]).dt.total_seconds() / 60.0

    study_end = pd.Timestamp.now(tz="UTC").tz_localize(None)
    transfer_naive = (df["transfer_ts"].dt.tz_localize(None)
                      if df["transfer_ts"].dt.tz is not None else df["transfer_ts"])
    censored = df["event_occurred"] == 0
    df.loc[censored, "duration"] = (
        (study_end - transfer_naive[censored]).dt.total_seconds() / 60.0
    )
    df["duration"] = df["duration"].clip(lower=1.0, upper=480.0)
    df = df[df["duration"].notna() & (df["duration"] > 0)]

    print(f"[SurvivalTime] Prepared {len(df)} records | "
          f"events: {df['event_occurred'].sum()} | "
          f"censored: {(df['event_occurred'] == 0).sum()}")
    return df[["duration", "event_occurred"]]


def train_survival_model(df, save: bool = True):
    """Fits a KaplanMeierFitter. For the full pipeline use ml_engine/train_models.py."""
    from lifelines import KaplanMeierFitter

    kmf = KaplanMeierFitter()
    kmf.fit(durations=df["duration"], event_observed=df["event_occurred"],
            label="Mule Withdrawal Time (mins)")
    if save:
        os.makedirs(WEIGHTS_DIR, exist_ok=True)
        with open(KM_MODEL_PATH, "wb") as f:
            pickle.dump(kmf, f)
        print(f"[SurvivalTime] Model saved to {KM_MODEL_PATH}")
    print(f"[SurvivalTime] Median cashout time: {kmf.median_survival_time_:.1f} minutes")
    return kmf


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    now_iso = datetime.now(timezone.utc).isoformat()
    print("\n[TEST] Same timestamp, different case profiles - windows should DIFFER "
          "if Cox PH is active:\n")
    for label, kw in [
        ("Small daytime transfer, tier 1", dict(amount=60000, mule_tier=1, nearest_travel_mins=12)),
        ("Large night transfer, tier 2  ", dict(amount=2400000, mule_tier=2, nearest_travel_mins=3)),
    ]:
        r = predict_time_window(transaction_timestamp=now_iso,
                               mule_account_id="ACC_MULE_0042", **kw)
        print(f"  {label} -> {r['start_ist']}-{r['end_ist']} IST "
              f"| {r['window_minutes']} min wide | conf {r['confidence']} | {r['model_source']}")
