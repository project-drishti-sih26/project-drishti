"""
Project Drishti — ML Engine
File: ml_engine/pipelines/spatial_filter.py
Role: Role 2 — ML/AI Engineer

STEP 1 of WHERE Engine: Candidate Retrieval.
Prunes all ATMs down to only those physically reachable by road
within the predicted cashout time window.

Uses Uber H3 spatial indexing for fast hex-based candidate retrieval.
Falls back to Haversine bounding-box if H3 is unavailable.
"""

import os
import math
import json
from typing import List, Dict, Any, Optional

# ─── Configuration ─────────────────────────────────────────────────────────────
H3_RESOLUTION = 9           # H3 level 9 ≈ avg edge length ~0.17 km
MAX_TRAVEL_TIME_MINS = 45   # Only ATMs reachable within 45 minutes
URBAN_SPEED_KMPH = 28       # Avg urban road speed (Delhi/Mumbai traffic)
ROAD_FACTOR = 1.35          # Road distance ≈ 1.35× straight-line (Haversine)

ATM_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "simulation", "data", "atms_master.csv"
)
DISTANCE_MATRIX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "simulation", "data", "distance_matrix.json"
)

# ─── Lazy-loaded module-level cache ───────────────────────────────────────────
_atm_df = None
_distance_matrix: Dict = {}


def _load_data():
    """Loads ATM CSV and distance matrix ONCE at first call."""
    global _atm_df, _distance_matrix

    if _atm_df is not None:
        return

    # ── Try loading from CSV (Role 5's output) ──────────────────────────
    try:
        import pandas as pd
        if os.path.exists(ATM_DATA_PATH):
            _atm_df = pd.read_csv(ATM_DATA_PATH)
            print(f"[SpatialFilter] Loaded {len(_atm_df)} ATMs from {ATM_DATA_PATH}")
        else:
            print("[SpatialFilter] atms_master.csv not found. Using built-in DEMO dataset.")
            _atm_df = _get_demo_atm_dataframe()

        if os.path.exists(DISTANCE_MATRIX_PATH):
            with open(DISTANCE_MATRIX_PATH, "r") as f:
                _distance_matrix = json.load(f)
            print(f"[SpatialFilter] Loaded distance matrix with {len(_distance_matrix)} entries.")

    except ImportError:
        print("[SpatialFilter] pandas not installed. Using built-in DEMO dataset (list mode).")
        _atm_df = _get_demo_atm_list()


def _get_demo_atm_list() -> List[Dict]:
    """
    Built-in demo ATM data for Delhi NCR.
    Used when atms_master.csv is not yet available (Role 5 still working).
    This lets the ML pipeline run end-to-end immediately on Day 1.
    """
    return [
        {"location_id": "ATM_SBI_CP_001",    "bank_name": "SBI",    "latitude": 28.6315, "longitude": 77.2167, "address": "Connaught Place, New Delhi",     "h3_index": "891f19464c3ffff", "historical_fraud_count": 6,  "is_active": True},
        {"location_id": "ATM_HDFC_KB_002",   "bank_name": "HDFC",   "latitude": 28.6520, "longitude": 77.1900, "address": "Karol Bagh, New Delhi",           "h3_index": "891f19466c3ffff", "historical_fraud_count": 2,  "is_active": True},
        {"location_id": "ATM_PNB_LN_003",    "bank_name": "PNB",    "latitude": 28.5700, "longitude": 77.2400, "address": "Lajpat Nagar, New Delhi",         "h3_index": "891f1945cc3ffff", "historical_fraud_count": 4,  "is_active": True},
        {"location_id": "ATM_AXIS_DL_004",   "bank_name": "Axis",   "latitude": 28.6800, "longitude": 77.2300, "address": "Civil Lines, New Delhi",           "h3_index": "891f1947ec3ffff", "historical_fraud_count": 1,  "is_active": True},
        {"location_id": "ATM_ICICI_PM_005",  "bank_name": "ICICI",  "latitude": 28.5500, "longitude": 77.2000, "address": "Panchsheel Marg, New Delhi",      "h3_index": "891f1945103ffff", "historical_fraud_count": 3,  "is_active": True},
        {"location_id": "ATM_BOB_MG_006",    "bank_name": "BOB",    "latitude": 28.6200, "longitude": 77.3500, "address": "Mayur Vihar, New Delhi",           "h3_index": "891f19450c3ffff", "historical_fraud_count": 5,  "is_active": True},
        {"location_id": "ATM_UBI_NR_007",    "bank_name": "UBI",    "latitude": 28.7040, "longitude": 77.1022, "address": "Nangloi, New Delhi",               "h3_index": "891f19432c3ffff", "historical_fraud_count": 7,  "is_active": True},
        {"location_id": "ATM_SBI_DW_008",    "bank_name": "SBI",    "latitude": 28.5921, "longitude": 77.0460, "address": "Dwarka Sector 10, New Delhi",     "h3_index": "891f1950cc3ffff", "historical_fraud_count": 3,  "is_active": True},
        {"location_id": "ATM_HDFC_RK_009",   "bank_name": "HDFC",   "latitude": 28.6129, "longitude": 77.2295, "address": "Rajiv Chowk, New Delhi",          "h3_index": "891f19464c3ffff", "historical_fraud_count": 8,  "is_active": True},
        {"location_id": "ATM_PNB_JP_010",    "bank_name": "PNB",    "latitude": 28.5355, "longitude": 77.3910, "address": "Jasola, New Delhi",               "h3_index": "891f19448c3ffff", "historical_fraud_count": 0,  "is_active": True},
        {"location_id": "ATM_AXIS_GK_011",   "bank_name": "Axis",   "latitude": 28.5400, "longitude": 77.2400, "address": "Greater Kailash, New Delhi",      "h3_index": "891f1945dc3ffff", "historical_fraud_count": 2,  "is_active": True},
        {"location_id": "ATM_SBI_SHD_012",   "bank_name": "SBI",    "latitude": 28.6700, "longitude": 77.2900, "address": "Shahdara, New Delhi",             "h3_index": "891f19478c3ffff", "historical_fraud_count": 5,  "is_active": True},
        {"location_id": "ATM_ICICI_VK_013",  "bank_name": "ICICI",  "latitude": 28.6450, "longitude": 77.3300, "address": "Vikaspuri, New Delhi",            "h3_index": "891f19442c3ffff", "historical_fraud_count": 1,  "is_active": False}, # Inactive
        {"location_id": "ATM_HDFC_ND_014",   "bank_name": "HDFC",   "latitude": 28.5850, "longitude": 77.1500, "address": "Vasant Kunj, New Delhi",          "h3_index": "891f19510c3ffff", "historical_fraud_count": 4,  "is_active": True},
        {"location_id": "ATM_PNB_MX_015",    "bank_name": "PNB",    "latitude": 28.7500, "longitude": 77.1200, "address": "Model Town, New Delhi",           "h3_index": "891f19420c3ffff", "historical_fraud_count": 6,  "is_active": True},
    ]


def _get_demo_atm_dataframe():
    """Returns demo ATMs as a pandas DataFrame."""
    import pandas as pd
    return pd.DataFrame(_get_demo_atm_list())


# ─── Core Geometry ─────────────────────────────────────────────────────────────
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance in km between two GPS coordinates (Haversine formula)."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_travel_time(straight_km: float) -> float:
    """Estimates road travel time in minutes from straight-line distance."""
    road_km = straight_km * ROAD_FACTOR
    return (road_km / URBAN_SPEED_KMPH) * 60


# ─── Main Public Function ──────────────────────────────────────────────────────
def get_candidate_atms(
    mule_latitude: float,
    mule_longitude: float,
    max_travel_minutes: float = MAX_TRAVEL_TIME_MINS,
) -> List[Dict[str, Any]]:
    """
    Returns all ATMs reachable within `max_travel_minutes` from the mule's
    last known GPS location.

    Tries H3-based retrieval first (fast). Falls back to Haversine bounding
    box if h3 library is not installed.

    Args:
        mule_latitude:     Mule's last known latitude.
        mule_longitude:    Mule's last known longitude.
        max_travel_minutes: Maximum road travel time filter (default 45 min).

    Returns:
        List of ATM candidate dicts, each with added 'distance_km' and
        'travel_time_mins' fields. Inactive ATMs are excluded.
    """
    _load_data()

    # ── Get the raw ATM list ───────────────────────────────────────────────
    try:
        import pandas as pd
        if isinstance(_atm_df, pd.DataFrame):
            raw_atms = _atm_df.to_dict(orient="records")
        else:
            raw_atms = _atm_df  # Already a list (no-pandas fallback)
    except ImportError:
        raw_atms = _atm_df

    # ── Filter inactive ATMs ───────────────────────────────────────────────
    active_atms = [a for a in raw_atms if a.get("is_active", True)]

    # ── Try H3-based retrieval ────────────────────────────────────────────
    candidates = []
    try:
        import h3
        candidates = _filter_by_h3(active_atms, mule_latitude, mule_longitude, max_travel_minutes)
        print(f"[SpatialFilter] H3 retrieval: {len(candidates)} candidates found.")
    except ImportError:
        # H3 not installed — fall back to Haversine bounding box
        candidates = _filter_by_haversine(active_atms, mule_latitude, mule_longitude, max_travel_minutes)
        print(f"[SpatialFilter] Haversine fallback: {len(candidates)} candidates found.")

    # ── Safety: always return at least 5 ATMs (extend radius if needed) ──
    if len(candidates) < 5 and active_atms:
        print("[SpatialFilter] WARNING: Fewer than 5 candidates. Extending search to all active ATMs.")
        candidates = _filter_by_haversine(active_atms, mule_latitude, mule_longitude, 999)

    return candidates


def _filter_by_h3(
    atms: List[Dict],
    mule_lat: float,
    mule_lon: float,
    max_travel_minutes: float,
) -> List[Dict]:
    """H3-based filtering using k-ring expansion."""
    import h3

    # Max straight-line search radius from travel time budget
    max_straight_km = (max_travel_minutes / 60) * URBAN_SPEED_KMPH / ROAD_FACTOR

    mule_h3 = h3.latlng_to_cell(mule_lat, mule_lon, H3_RESOLUTION)
    avg_edge_km = h3.average_hexagon_edge_length(H3_RESOLUTION, unit="km")
    k = max(1, int(max_straight_km / avg_edge_km))
    nearby_hexes = h3.grid_disk(mule_h3, k)

    candidates = []
    for atm in atms:
        atm_h3 = atm.get("h3_index")
        straight_km = haversine_km(mule_lat, mule_lon, atm["latitude"], atm["longitude"])
        travel_mins = estimate_travel_time(straight_km)

        # Accept if ATM is in a nearby hex AND within travel time budget
        in_hex_range = (atm_h3 in nearby_hexes) if atm_h3 else True
        if in_hex_range and travel_mins <= max_travel_minutes:
            enriched = dict(atm)
            enriched["distance_km"] = round(straight_km * ROAD_FACTOR, 2)
            enriched["travel_time_mins"] = round(travel_mins, 1)
            candidates.append(enriched)

    return candidates


def _filter_by_haversine(
    atms: List[Dict],
    mule_lat: float,
    mule_lon: float,
    max_travel_minutes: float,
) -> List[Dict]:
    """Simple Haversine distance-based filtering (H3 fallback)."""
    candidates = []
    for atm in atms:
        straight_km = haversine_km(mule_lat, mule_lon, atm["latitude"], atm["longitude"])
        travel_mins = estimate_travel_time(straight_km)
        if travel_mins <= max_travel_minutes:
            enriched = dict(atm)
            enriched["distance_km"] = round(straight_km * ROAD_FACTOR, 2)
            enriched["travel_time_mins"] = round(travel_mins, 1)
            candidates.append(enriched)
    return candidates


# ─── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Mule last seen near Connaught Place, New Delhi
    MULE_LAT, MULE_LON = 28.6315, 77.2167

    print(f"\n[TEST] Finding ATM candidates within 45 min of ({MULE_LAT}, {MULE_LON})")
    candidates = get_candidate_atms(MULE_LAT, MULE_LON, max_travel_minutes=45)

    print(f"\n[RESULTS] {len(candidates)} candidate ATMs found:\n")
    for atm in sorted(candidates, key=lambda x: x["travel_time_mins"]):
        active_tag = "ACTIVE" if atm.get("is_active", True) else "INACTIVE"
        print(f"  [{active_tag}] {atm['bank_name']:6} | {atm['address']:<40} | "
              f"{atm['travel_time_mins']:5.1f} min | "
              f"Fraud history: {atm['historical_fraud_count']}")
