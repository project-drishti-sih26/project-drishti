"""
FILE: ml_engine/pipelines/spatial_filter.py
ROLE: Role 2 — ML/AI Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the WHERE Engine Phase 1: Candidate Retrieval. It uses Uber's H3
    hexagonal spatial indexing to rapidly prune the full ATM universe
    (from simulation/data/atms_master.csv) down to only the ~100-200 ATMs
    that a mule runner can physically reach by road within the predicted
    cashout time window.

    Without this step, the LambdaMART ranker would need to score 100,000+
    ATMs — that's too slow. By filtering first (this step) and then ranking
    (ltr_ranker.py), we achieve sub-second total prediction latency.

📌 WHY IS THIS FILE NEEDED?
    Geography is a hard constraint. A mule in Karol Bagh (New Delhi) cannot
    reach an ATM in Bandra (Mumbai) in 30 minutes. The Spatial Filter enforces
    physical reality — it discards all geographically impossible candidates
    BEFORE the expensive ML ranking step runs. This is called the
    "Candidate Retrieval" phase of a Retrieval + Ranking pipeline
    (same architecture used by Google Maps, Uber, and recommendation systems).

📌 WHAT TO IMPLEMENT HERE:

    CONSTANTS (tune these as needed):
    - H3_RESOLUTION = 9         # H3 level 9 hexes ≈ 0.1 km² each (very granular)
    - SEARCH_RADIUS_KM = 10.0   # Search within 10 km road radius
    - MAX_TRAVEL_TIME_MINS = 45 # Only include ATMs reachable within 45 minutes
    - ATM_DATA_PATH = "simulation/data/atms_master.csv"
    - DISTANCE_MATRIX_PATH = "simulation/data/distance_matrix.json"

    DATA LOADING (run once at module import, not per-request):
    Load atms_master.csv into a pandas DataFrame when the module is imported.
    Load distance_matrix.json into a dict.
    This avoids reading the file from disk for every prediction request.
    Use module-level variables: `_atm_df = None` and `_distance_matrix = None`
    with a `_load_data()` function that lazy-loads on first call.

    MAIN FUNCTION:
    def get_candidate_atms(
        mule_latitude: float,
        mule_longitude: float,
        max_travel_minutes: float = MAX_TRAVEL_TIME_MINS
    ) -> list[dict]:
        """
        Finds all ATMs reachable within `max_travel_minutes` from the
        mule's last known location.

        APPROACH:
        OPTION A — H3 K-Ring approach (preferred, faster):
            1. Convert mule's lat/lng to H3 index at H3_RESOLUTION:
               mule_h3 = h3.latlng_to_cell(mule_latitude, mule_longitude, H3_RESOLUTION)
            2. Get all H3 cells within k rings from mule's cell:
               k = int(SEARCH_RADIUS_KM / h3.average_hexagon_edge_length(H3_RESOLUTION, unit='km'))
               nearby_hexes = h3.grid_disk(mule_h3, k)
            3. Filter the ATM DataFrame to only ATMs whose h3_index is in nearby_hexes:
               candidate_atms = _atm_df[_atm_df['h3_index'].isin(nearby_hexes)]

        OPTION B — Bounding Box + Distance Matrix (simpler fallback):
            1. Create a lat/lng bounding box around the mule (±0.1 degrees ≈ ±11 km).
            2. Filter ATMs within the bounding box from the DataFrame.
            3. Use the precomputed distance matrix to filter by travel time.

        For each candidate ATM, compute road travel time:
            If distance_matrix has the entry: use it directly.
            If not in matrix: estimate using Haversine formula:
                distance_km = haversine(mule_lat, mule_lng, atm_lat, atm_lng)
                travel_time = (distance_km / 30) * 60  # Assume 30 km/h average urban speed

        Filter: only keep ATMs where travel_time_mins <= max_travel_minutes.

        For each passing ATM, build a dict:
        {
            "location_id": str,
            "bank_name": str,
            "latitude": float,
            "longitude": float,
            "address": str,
            "h3_index": str,
            "historical_fraud_count": int,
            "distance_km": float,
            "travel_time_mins": float,
            "is_active": bool
        }

        Filter out inactive ATMs (is_active == False).
        Return the list of candidate dicts.
        Log how many candidates were found: print(f"[Spatial] Found {len(candidates)} candidates")
        """

    HELPER FUNCTION:
    def haversine_distance(lat1, lon1, lat2, lon2) -> float:
        """
        Computes straight-line distance in km between two GPS coordinates.
        Uses the Haversine formula. This is the fallback when distance
        matrix doesn't have a specific entry.
        Note: Haversine gives straight-line distance. Real road distance
        is typically 1.3-1.5x the straight-line distance (urban factor).
        """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called BY: ml_engine/pipelines/inference_pipeline.py (STEP 1).
    - Reads FROM: simulation/data/atms_master.csv (Role 5's output).
    - Reads FROM: simulation/data/distance_matrix.json (Role 5's output).
    - Output is passed to: ltr_ranker.py or fallback_heuristic.py for ranking.

📌 LIBRARIES TO USE:
    - h3 (pip install h3) — Uber's H3 spatial library
    - pandas — for loading and filtering the ATM CSV
    - json — for loading the distance matrix
    - math (radians, cos, sin, atan2, sqrt) — for Haversine formula
    - os (for building file paths)
"""
