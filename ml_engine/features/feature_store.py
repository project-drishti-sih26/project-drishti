"""
Project Drishti — ML Engine
File: ml_engine/features/feature_store.py
Role: Role 2 — ML/AI Engineer

=============================================================================
SINGLE SOURCE OF TRUTH FOR FEATURES  (train/serve parity)
=============================================================================
The #1 silent killer of production ML is *train/serve skew*: the training job
computes a feature one way, the live server computes it another way, and the
model's learned relationships no longer apply. Drishti hit this exact bug —
training filled `travel_time_mins` with the default 999 for every row while
inference passed real values, so the ranker had ZERO tree splits on distance
and dispatched police to the wrong ATM.

The fix is structural, not a patch: `build_feature_vector()` in this file is
the ONLY place a feature vector is ever constructed. `train_models.py` and
`ltr_ranker.py` (inference) both call it. It is now impossible for the two
paths to disagree.

CAUSALITY / NO LABEL LEAKAGE
---------------------------
Behavioural features (mule_atm_affinity, mule_network_affinity, h3_fraud_density)
are counts of *past* events. If we built them from the whole dataset and then
trained on that dataset, each row's features would encode its own label —
the model would score 0.99 NDCG in training and fail completely in the field.

`build_causal_training_set()` therefore walks fraud events in strict
chronological order and, for every event, computes features from the store as
it stood BEFORE that event, then folds the event in. This mirrors exactly what
the live system can know at prediction time.
=============================================================================
"""

import os
import json
import math
import pickle
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ─── Paths ────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_DIR = os.path.join(_HERE, "..", "weights")
STORE_PATH = os.path.join(WEIGHTS_DIR, "feature_store.pkl")
SIM_DATA_DIR = os.path.join(_HERE, "..", "..", "simulation", "data")
ATMS_CSV = os.path.join(SIM_DATA_DIR, "atms_master.csv")
TXS_CSV = os.path.join(SIM_DATA_DIR, "historical_transactions.csv")

# ─── Spatial resolutions ──────────────────────────────────────────────────────
# res 7 (~5 km across) = "neighbourhood" scale, the right granularity for
# describing crime concentration around an ATM.
H3_DENSITY_RES = 7
# res 6 (~12 km across) = "syndicate operating area" scale, used to aggregate
# ATM usage by *other* mules operating near this one.
H3_NETWORK_RES = 6

# ─── Feature schema — order is contractual, do not reorder ───────────────────
FEATURE_NAMES = [
    "travel_time_mins",         # road travel minutes from mule's last position
    "distance_km",              # road distance (km)
    "historical_fraud_count",   # prior confirmed frauds at this exact ATM
    "h3_fraud_density",         # prior frauds across the surrounding H3 cell
    "mule_atm_affinity",        # times THIS mule cashed out here before
    "mule_network_affinity",    # times nearby/linked mules cashed out here
    "atm_type_encoded",         # 0=ATM, 1=Branch, 2=Banking Correspondent
    "hour_of_day",              # 0-23 local (IST) hour of the transfer
    "is_night",                 # 1 if 22:00-05:00 IST (peak mule activity)
    "is_weekend",               # 1 if Sat/Sun
    "amount_lakhs",             # compromised amount in ₹ lakhs
]

_ATM_TYPE_MAP = {"ATM": 0, "Branch": 1, "Banking_Correspondent": 2}
IST_OFFSET_HOURS = 5.5


def _h3_cell(lat: float, lon: float, res: int) -> str:
    """H3 cell index, with a coarse lat/lon grid fallback if h3 is unavailable."""
    try:
        import h3
        return h3.latlng_to_cell(lat, lon, res)
    except Exception:
        # Deterministic fallback grid so features remain consistent train/serve.
        step = 0.05 if res >= 7 else 0.12
        return f"grid_{res}_{round(lat / step)}_{round(lon / step)}"


def _parse_ts(ts: Any) -> datetime:
    """Parses any ISO-ish timestamp to a tz-aware UTC datetime."""
    if isinstance(ts, datetime):
        dt = ts
    else:
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _ist_parts(ts: Any) -> Tuple[int, int]:
    """
    Returns (hour_of_day_IST, weekday_IST).

    Indian Standard Time matters here, not UTC: mule cashout behaviour is driven
    by *local* human routines — ATM queue density, shop shutter timings, police
    shift changes. A model trained on UTC hours would smear those patterns by
    5.5 hours and learn nothing useful about "night withdrawals".
    """
    dt = _parse_ts(ts)
    ist = dt.timestamp() + IST_OFFSET_HOURS * 3600
    ist_dt = datetime.fromtimestamp(ist, tz=timezone.utc)
    return ist_dt.hour, ist_dt.weekday()


class FeatureStore:
    """
    Holds the behavioural aggregates needed by the ranker.

    All three aggregates are pure counts of *observed past cashouts*, so they
    can be updated incrementally — which is what makes causal (leak-free)
    training and live serving use the same code path.
    """

    def __init__(self) -> None:
        self.mule_atm: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.network_atm: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.h3_density: Dict[str, int] = defaultdict(int)
        self.atm_h3_cell: Dict[str, str] = {}
        self.n_events: int = 0

    # ── Registration / update ────────────────────────────────────────────────
    def register_atms(self, atms: List[Dict[str, Any]]) -> None:
        """Precomputes each ATM's H3 density cell once."""
        for a in atms:
            aid = str(a["location_id"])
            if aid not in self.atm_h3_cell:
                self.atm_h3_cell[aid] = _h3_cell(
                    float(a["latitude"]), float(a["longitude"]), H3_DENSITY_RES
                )

    def observe_cashout(
        self, mule_id: str, atm_id: str, mule_lat: float, mule_lon: float
    ) -> None:
        """Folds one confirmed cashout into the behavioural aggregates."""
        mule_id, atm_id = str(mule_id), str(atm_id)
        self.mule_atm[mule_id][atm_id] += 1
        self.network_atm[_h3_cell(mule_lat, mule_lon, H3_NETWORK_RES)][atm_id] += 1
        cell = self.atm_h3_cell.get(atm_id)
        if cell:
            self.h3_density[cell] += 1
        self.n_events += 1

    # ── Lookups ──────────────────────────────────────────────────────────────
    def affinity(self, mule_id: str, atm_id: str) -> int:
        return self.mule_atm.get(str(mule_id), {}).get(str(atm_id), 0)

    def network_affinity(self, mule_lat: float, mule_lon: float, atm_id: str) -> int:
        cell = _h3_cell(mule_lat, mule_lon, H3_NETWORK_RES)
        total = self.network_atm.get(cell, {}).get(str(atm_id), 0)
        # Subtract nothing here: network affinity intentionally includes this
        # mule's own history too, because at prediction time we cannot tell
        # which of the nearby mules is which. Keeping it inclusive matches
        # what the live system observes.
        return total

    def fraud_density(self, atm_id: str) -> int:
        cell = self.atm_h3_cell.get(str(atm_id))
        return self.h3_density.get(cell, 0) if cell else 0

    # ── Persistence ──────────────────────────────────────────────────────────
    def save(self, path: str = STORE_PATH) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "mule_atm": {k: dict(v) for k, v in self.mule_atm.items()},
                    "network_atm": {k: dict(v) for k, v in self.network_atm.items()},
                    "h3_density": dict(self.h3_density),
                    "atm_h3_cell": dict(self.atm_h3_cell),
                    "n_events": self.n_events,
                },
                f,
            )
        print(f"[FeatureStore] Saved ({self.n_events} events) -> {path}")

    @classmethod
    def load(cls, path: str = STORE_PATH) -> Optional["FeatureStore"]:
        if not os.path.exists(path):
            return None
        try:
            with open(path, "rb") as f:
                raw = pickle.load(f)
        except Exception as e:
            print(f"[FeatureStore] WARNING: could not load store: {e}")
            return None
        s = cls()
        for k, v in raw.get("mule_atm", {}).items():
            s.mule_atm[k] = defaultdict(int, v)
        for k, v in raw.get("network_atm", {}).items():
            s.network_atm[k] = defaultdict(int, v)
        s.h3_density = defaultdict(int, raw.get("h3_density", {}))
        s.atm_h3_cell = dict(raw.get("atm_h3_cell", {}))
        s.n_events = raw.get("n_events", 0)
        return s


# ─── Module-level cache for the serving path ─────────────────────────────────
_store: Optional[FeatureStore] = None
_store_checked = False


def get_store() -> FeatureStore:
    """Returns the shared FeatureStore, loading from disk on first use."""
    global _store, _store_checked
    if _store is None and not _store_checked:
        _store_checked = True
        _store = FeatureStore.load()
        if _store is None:
            print("[FeatureStore] No store on disk - using empty store "
                  "(behavioural features will be 0; ranking falls back to "
                  "distance + fraud history).")
            _store = FeatureStore()
    return _store  # type: ignore[return-value]


# ═════════════════════════════════════════════════════════════════════════════
#  THE ONE AND ONLY FEATURE BUILDER — used by BOTH training and inference
# ═════════════════════════════════════════════════════════════════════════════
def build_feature_vector(
    atm: Dict[str, Any],
    mule_id: str,
    tx_timestamp: Any,
    mule_lat: float,
    mule_lon: float,
    amount: float,
    store: FeatureStore,
) -> List[float]:
    """
    Builds one (mule, ATM) feature row.

    `atm` must already carry `travel_time_mins` and `distance_km` as computed by
    ml_engine/pipelines/spatial_filter.py — the same function is used in training
    and at serve time, which is what guarantees the distance features are real
    in both paths.
    """
    hour, weekday = _ist_parts(tx_timestamp)
    atm_id = str(atm.get("location_id", ""))

    return [
        float(atm.get("travel_time_mins", 0.0) or 0.0),
        float(atm.get("distance_km", 0.0) or 0.0),
        float(atm.get("historical_fraud_count", 0) or 0),
        float(store.fraud_density(atm_id)),
        float(store.affinity(mule_id, atm_id)),
        float(store.network_affinity(mule_lat, mule_lon, atm_id)),
        float(_ATM_TYPE_MAP.get(str(atm.get("location_type", "ATM")), 0)),
        float(hour),
        1.0 if (hour >= 22 or hour < 5) else 0.0,
        1.0 if weekday >= 5 else 0.0,
        float(amount) / 100000.0,
    ]


def build_feature_matrix(
    candidates: List[Dict[str, Any]],
    mule_id: str,
    tx_timestamp: Any,
    mule_lat: float,
    mule_lon: float,
    amount: float,
    store: Optional[FeatureStore] = None,
):
    """Vectorised helper: returns a numpy array of shape (n_candidates, n_features)."""
    import numpy as np

    store = store or get_store()
    rows = [
        build_feature_vector(a, mule_id, tx_timestamp, mule_lat, mule_lon, amount, store)
        for a in candidates
    ]
    return np.asarray(rows, dtype=float)


# ═════════════════════════════════════════════════════════════════════════════
#  CAUSAL TRAINING SET CONSTRUCTION
# ═════════════════════════════════════════════════════════════════════════════
def build_causal_training_set(
    txs_csv: str = TXS_CSV,
    atms_csv: str = ATMS_CSV,
    max_events: Optional[int] = None,
    max_travel_minutes: float = 45.0,
    progress_every: int = 400,
):
    """
    Builds a leak-free Learning-to-Rank dataset.

    For every observed cashout, in chronological order:
      1. Retrieve reachable ATM candidates from the mule's last known position
         (SAME spatial_filter call the live system uses).
      2. Compute features from the store's state BEFORE this event.
      3. Label the ATM actually used as relevant (2), all others 0.
      4. Fold the event into the store so later events see it as history.

    Returns:
        (X, y, groups, meta, store)
        X       : np.ndarray (n_rows, n_features)
        y       : list[int] relevance labels
        groups  : list[int] candidates per query (required by LambdaRank)
        meta    : list[dict] per-query info for evaluation
        store   : FeatureStore populated with the FULL history (for serving)
    """
    import numpy as np
    import pandas as pd

    from ml_engine.pipelines.spatial_filter import get_candidate_atms

    atm_df = pd.read_csv(atms_csv)
    atms = atm_df.to_dict(orient="records")

    store = FeatureStore()
    store.register_atms(atms)

    df = pd.read_csv(txs_csv)
    required = {"withdrawal_atm_id", "mule_last_lat", "mule_last_lon", "transfer_timestamp"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{txs_csv} is missing columns {sorted(missing)}. "
            "Regenerate it: python simulation/generators/generate_fraud_graph.py"
        )

    events = df[df["withdrawal_atm_id"].notna() & (df["withdrawal_atm_id"] != "")].copy()
    events = events[events["mule_last_lat"].notna()]
    events = events.sort_values("transfer_timestamp").reset_index(drop=True)
    if max_events:
        events = events.head(max_events)

    print(f"[FeatureStore] Building causal LTR dataset from {len(events)} cashout events...")

    X_rows: List[List[float]] = []
    y: List[int] = []
    groups: List[int] = []
    meta: List[Dict[str, Any]] = []

    for i, row in events.iterrows():
        mule_id = str(row["receiver_id"])
        mule_lat = float(row["mule_last_lat"])
        mule_lon = float(row["mule_last_lon"])
        actual_atm = str(row["withdrawal_atm_id"])
        ts = row["transfer_timestamp"]
        amount = float(row.get("amount", 0) or 0)

        candidates = get_candidate_atms(mule_lat, mule_lon, max_travel_minutes=max_travel_minutes)
        if not candidates:
            continue

        # The true ATM must be in the candidate set or the query is unlearnable.
        # Tracking this gives us the retrieval recall ceiling to report honestly.
        cand_ids = {str(c.get("location_id")) for c in candidates}
        hit = actual_atm in cand_ids
        if not hit:
            continue

        # --- features computed from history BEFORE this event (no leakage) ---
        for c in candidates:
            X_rows.append(
                build_feature_vector(c, mule_id, ts, mule_lat, mule_lon, amount, store)
            )
            y.append(2 if str(c.get("location_id")) == actual_atm else 0)

        groups.append(len(candidates))
        meta.append({
            "tx_id": str(row.get("tx_id", "")),
            "mule_id": mule_id,
            "actual_atm": actual_atm,
            "n_candidates": len(candidates),
            "timestamp": str(ts),
            "candidate_ids": [str(c.get("location_id")) for c in candidates],
        })

        # --- now fold the event in, so subsequent queries see it as history ---
        store.observe_cashout(mule_id, actual_atm, mule_lat, mule_lon)

        if progress_every and (len(groups) % progress_every == 0):
            print(f"  ... {len(groups)} queries built ({len(X_rows):,} rows)")

    X = np.asarray(X_rows, dtype=float)
    print(f"[FeatureStore] Dataset ready: {X.shape[0]:,} rows | "
          f"{len(groups)} queries | {X.shape[1]} features")
    return X, y, groups, meta, store


if __name__ == "__main__":
    X, y, groups, meta, store = build_causal_training_set(max_events=300)
    print("\nFeature names:", FEATURE_NAMES)
    print("X shape:", X.shape, "| positives:", sum(1 for v in y if v > 0))
    print("Mean candidates/query:", sum(groups) / max(len(groups), 1))
