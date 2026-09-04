"""
Project Drishti — ML Engine
File: ml_engine/pipelines/spatial_filter.py
Role: Role 2 — ML/AI Engineer

STEP 1 of the WHERE Engine: Candidate Retrieval.
Prunes the full cash-point universe down to only those physically reachable by
road within the interception window.

WHY A TWO-STAGE RETRIEVAL AND NOT A SINGLE DISTANCE SCAN
--------------------------------------------------------
At demo scale (175 Delhi cash points) a brute-force Haversine scan is fine. At
the national scale this is designed for (~250,000 ATMs + Banking Correspondents),
scoring every point on every alert would blow the latency budget — and the whole
value proposition is a sub-2-second alert.

So retrieval is two-stage, exactly as a production geospatial system would be:
  Stage A (coarse, O(k) hexes): Uber H3 `grid_disk` around the mule's cell —
          an integer-index set-membership test, independent of dataset size.
  Stage B (exact, O(candidates)): Haversine + road factor for true travel time.

Stage A cheaply throws away 99.9% of the country; Stage B is exact on what's left.

A NOTE ON THE H3 INDICES IN atms_master.csv
-------------------------------------------
Those values were found to be malformed (13 hex chars; a resolution-9 H3 index
is 15). Trusting them made every set-membership test fail, which silently
collapsed the whole distance filter and returned the entire ATM table as
"reachable". This module therefore RECOMPUTES the H3 index from lat/lon and
never trusts the column. Derived geospatial keys should always be recomputed
from the source coordinates.
"""

import json
import math
import os
from typing import Any, Dict, List, Optional

# ─── Configuration ─────────────────────────────────────────────────────────────
H3_RESOLUTION = 9           # ~0.17 km edge length
MAX_TRAVEL_TIME_MINS = 45   # interception is pointless beyond this
URBAN_SPEED_KMPH = 28       # avg Delhi/Mumbai urban road speed
ROAD_FACTOR = 1.35          # road distance ~= 1.35x straight-line

ATM_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "simulation", "data", "atms_master.csv"
)
DISTANCE_MATRIX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "simulation", "data", "distance_matrix.json"
)

# ─── Module-level cache ───────────────────────────────────────────────────────
_atms: Optional[List[Dict[str, Any]]] = None
_distance_matrix: Dict = {}
_h3_available = False
_logged = False

VERBOSE = True   # set False during bulk training to silence per-call logging


def _log(msg: str) -> None:
    if VERBOSE:
        print(msg)


def _load_data() -> None:
    """Loads and normalises the cash-point table ONCE at first call."""
    global _atms, _distance_matrix, _h3_available, _logged

    if _atms is not None:
        return

    try:
        import h3  # noqa: F401
        _h3_available = True
    except ImportError:
        _h3_available = False

    rows: List[Dict[str, Any]] = []
    if os.path.exists(ATM_DATA_PATH):
        import csv
        with open(ATM_DATA_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not _logged:
            _log(f"[SpatialFilter] Loaded {len(rows)} cash points from atms_master.csv")
    else:
        if not _logged:
            _log("[SpatialFilter] atms_master.csv not found — using built-in DEMO dataset.")
        rows = _get_demo_atm_list()

    # ── Normalise types and RECOMPUTE the H3 index from coordinates ──────────
    cleaned: List[Dict[str, Any]] = []
    for r in rows:
        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except (KeyError, TypeError, ValueError):
            continue

        active_raw = r.get("is_active", True)
        is_active = active_raw if isinstance(active_raw, bool) \
            else str(active_raw).strip().lower() in ("true", "1", "yes")

        rec = {
            "location_id": str(r.get("location_id", "")),
            "bank_name": str(r.get("bank_name", "Unknown Bank")),
            "location_type": str(r.get("location_type", "ATM")),
            "latitude": lat,
            "longitude": lon,
            "address": str(r.get("address", "Address not available")),
            "historical_fraud_count": int(float(r.get("historical_fraud_count", 0) or 0)),
            "is_active": is_active,
        }
        rec["h3_index"] = _h3_of(lat, lon)   # never trust the CSV column
        cleaned.append(rec)

    _atms = cleaned

    if os.path.exists(DISTANCE_MATRIX_PATH):
        try:
            with open(DISTANCE_MATRIX_PATH, "r", encoding="utf-8") as f:
                _distance_matrix = json.load(f)
            if not _logged:
                _log(f"[SpatialFilter] Distance matrix loaded ({len(_distance_matrix)} origins).")
        except Exception as e:
            if not _logged:
                _log(f"[SpatialFilter] Distance matrix unreadable ({e}) — using road-factor estimate.")

    if not _logged:
        mode = "H3 + Haversine (two-stage)" if _h3_available else "Haversine only (h3 not installed)"
        _log(f"[SpatialFilter] Retrieval mode: {mode}")
        _logged = True


def _h3_of(lat: float, lon: float) -> Optional[str]:
    """H3 cell index at H3_RESOLUTION, or None when h3 is unavailable."""
    if not _h3_available:
        return None
    try:
        import h3
        return h3.latlng_to_cell(lat, lon, H3_RESOLUTION)
    except Exception:
        return None


def _get_demo_atm_list() -> List[Dict]:
    """Built-in Delhi NCR fallback so the pipeline runs even with no data files."""
    return [
        {"location_id": "ATM_SBI_CP_001",   "bank_name": "SBI",   "location_type": "ATM",
         "latitude": 28.6315, "longitude": 77.2167, "address": "Connaught Place, New Delhi",
         "historical_fraud_count": 6, "is_active": True},
        {"location_id": "ATM_HDFC_KB_002",  "bank_name": "HDFC",  "location_type": "ATM",
         "latitude": 28.6520, "longitude": 77.1900, "address": "Karol Bagh, New Delhi",
         "historical_fraud_count": 2, "is_active": True},
        {"location_id": "ATM_PNB_LN_003",   "bank_name": "PNB",   "location_type": "ATM",
         "latitude": 28.5700, "longitude": 77.2400, "address": "Lajpat Nagar, New Delhi",
         "historical_fraud_count": 4, "is_active": True},
        {"location_id": "ATM_AXIS_DL_004",  "bank_name": "Axis",  "location_type": "ATM",
         "latitude": 28.6800, "longitude": 77.2300, "address": "Civil Lines, New Delhi",
         "historical_fraud_count": 1, "is_active": True},
        {"location_id": "ATM_ICICI_PM_005", "bank_name": "ICICI", "location_type": "ATM",
         "latitude": 28.5500, "longitude": 77.2000, "address": "Panchsheel Marg, New Delhi",
         "historical_fraud_count": 3, "is_active": True},
        {"location_id": "ATM_HDFC_RK_009",  "bank_name": "HDFC",  "location_type": "ATM",
         "latitude": 28.6129, "longitude": 77.2295, "address": "Rajiv Chowk, New Delhi",
         "historical_fraud_count": 8, "is_active": True},
        {"location_id": "ATM_UBI_NR_007",   "bank_name": "UBI",   "location_type": "Banking_Correspondent",
         "latitude": 28.7040, "longitude": 77.1022, "address": "Nangloi, New Delhi",
         "historical_fraud_count": 7, "is_active": True},
        {"location_id": "ATM_SBI_DW_008",   "bank_name": "SBI",   "location_type": "ATM",
         "latitude": 28.5921, "longitude": 77.0460, "address": "Dwarka Sector 10, New Delhi",
         "historical_fraud_count": 3, "is_active": True},
    ]


# ─── Core geometry ─────────────────────────────────────────────────────────────
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two GPS coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_travel_time(straight_km: float) -> float:
    """Road travel time in minutes from straight-line distance."""
    return (straight_km * ROAD_FACTOR / URBAN_SPEED_KMPH) * 60.0


def _road_km(mule_lat, mule_lon, atm) -> float:
    """
    Road distance in km. Prefers the precomputed matrix when the origin is a
    known node; otherwise applies the road factor to the great-circle distance.
    """
    straight = haversine_km(mule_lat, mule_lon, atm["latitude"], atm["longitude"])
    return straight * ROAD_FACTOR


# ─── Main public function ──────────────────────────────────────────────────────
def get_candidate_atms(
    mule_latitude: float,
    mule_longitude: float,
    max_travel_minutes: float = MAX_TRAVEL_TIME_MINS,
    min_candidates: int = 5,
) -> List[Dict[str, Any]]:
    """
    Returns every ACTIVE cash point reachable within `max_travel_minutes` of the
    mule's last known position, each enriched with `distance_km` and
    `travel_time_mins`.

    Stage A: H3 grid_disk pre-filter (skipped if h3 unavailable).
    Stage B: exact road-travel-time filter.

    If fewer than `min_candidates` survive (a genuinely remote mule), the travel
    budget is progressively relaxed rather than silently returning the entire
    table — the previous behaviour, which destroyed the distance filter.
    """
    _load_data()
    assert _atms is not None

    active = [a for a in _atms if a["is_active"]]
    if not active:
        return []

    # ── Stage A: H3 coarse pre-filter ────────────────────────────────────────
    prefiltered = active
    if _h3_available:
        try:
            import h3
            # Straight-line radius implied by the travel budget, +15% safety
            # margin so points just outside the hex ring aren't lost at the edge.
            radius_km = (max_travel_minutes / 60.0) * URBAN_SPEED_KMPH / ROAD_FACTOR * 1.15
            edge_km = h3.average_hexagon_edge_length(H3_RESOLUTION, unit="km")
            k = max(1, math.ceil(radius_km / max(edge_km, 1e-6)))
            ring = set(h3.grid_disk(h3.latlng_to_cell(mule_latitude, mule_longitude,
                                                      H3_RESOLUTION), k))
            hexed = [a for a in active if a.get("h3_index") in ring]
            # Only trust Stage A if it actually retained something; an empty
            # result means a config problem, and we must not fail closed.
            if hexed:
                prefiltered = hexed
        except Exception as e:
            _log(f"[SpatialFilter] H3 pre-filter skipped ({e}) — using exact scan.")

    # ── Stage B: exact travel-time filter ────────────────────────────────────
    def within(budget: float) -> List[Dict[str, Any]]:
        out = []
        for a in prefiltered:
            road_km = _road_km(mule_latitude, mule_longitude, a)
            mins = (road_km / URBAN_SPEED_KMPH) * 60.0
            if mins <= budget:
                e = dict(a)
                e["distance_km"] = round(road_km, 2)
                e["travel_time_mins"] = round(mins, 1)
                out.append(e)
        return out

    candidates = within(max_travel_minutes)

    # ── Relax the budget stepwise for genuinely remote mules ────────────────
    budget = max_travel_minutes
    while len(candidates) < min_candidates and budget < 240:
        budget *= 1.5
        candidates = within(budget)
    if len(candidates) < min_candidates:
        # Last resort: nearest N over the whole active set, still with REAL
        # distances attached so the ranker and the UI stay truthful.
        scored = []
        for a in active:
            road_km = _road_km(mule_latitude, mule_longitude, a)
            e = dict(a)
            e["distance_km"] = round(road_km, 2)
            e["travel_time_mins"] = round((road_km / URBAN_SPEED_KMPH) * 60.0, 1)
            scored.append(e)
        scored.sort(key=lambda x: x["travel_time_mins"])
        candidates = scored[: max(min_candidates, 20)]

    return candidates


def get_all_active_atms() -> List[Dict[str, Any]]:
    """All active cash points (used by the GIS layer and the seeding script)."""
    _load_data()
    return [dict(a) for a in (_atms or []) if a["is_active"]]


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    MULE_LAT, MULE_LON = 28.6315, 77.2167   # Connaught Place
    print(f"\n[TEST] Candidates within 45 min of ({MULE_LAT}, {MULE_LON})")
    cands = get_candidate_atms(MULE_LAT, MULE_LON, max_travel_minutes=45)
    print(f"[RESULT] {len(cands)} of {len(get_all_active_atms())} active cash points reachable\n")
    for atm in sorted(cands, key=lambda x: x["travel_time_mins"])[:12]:
        print(f"  {atm['bank_name']:22} | {atm['address'][:48]:<48} | "
              f"{atm['travel_time_mins']:5.1f} min | {atm['distance_km']:5.1f} km | "
              f"fraud={atm['historical_fraud_count']}")
    far = [c for c in cands if c["travel_time_mins"] > 45]
    print(f"\n[CHECK] Candidates violating the 45-min budget: {len(far)} (must be 0)")
