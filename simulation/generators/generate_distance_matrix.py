"""
Simulation Data Generator: Road Distance & Travel Time Matrix
Project Drishti — Role 5: Data Engineer

Computes precomputed road travel times (minutes) and road distances (km)
between H3 hex zones / ATM pairs across Delhi NCR.
Saves output to simulation/data/distance_matrix.json.
"""

import os
import csv
import json
import math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ATMS_PATH = os.path.join(DATA_DIR, "atms_master.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "distance_matrix.json")

URBAN_ROAD_FACTOR = 1.35  # Road distance vs straight-line (urban detour factor)
AVG_SPEED_KMPH = 28.0     # Average traffic speed across Delhi NCR (km/h)

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def generate_distance_matrix():
    if not os.path.exists(ATMS_PATH):
        raise FileNotFoundError(f"{ATMS_PATH} does not exist. Run generate_atms.py first.")

    with open(ATMS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        atms = list(reader)

    print(f"[INFO] Computing road distance matrix for {len(atms)} locations...")

    matrix = {}
    pair_count = 0

    for i, a1 in enumerate(atms):
        lat1 = float(a1["latitude"])
        lon1 = float(a1["longitude"])
        id1 = a1["location_id"]

        # Only compute pairs within 25 km to keep matrix compact and fast
        for j, a2 in enumerate(atms):
            if i == j:
                continue
            lat2 = float(a2["latitude"])
            lon2 = float(a2["longitude"])
            id2 = a2["location_id"]

            straight_km = haversine_km(lat1, lon1, lat2, lon2)
            if straight_km <= 25.0:
                road_km = round(straight_km * URBAN_ROAD_FACTOR, 2)
                travel_mins = round((road_km / AVG_SPEED_KMPH) * 60, 1)

                key = f"{id1}_TO_{id2}"
                matrix[key] = {
                    "distance_km": road_km,
                    "travel_time_mins": travel_mins
                }
                pair_count += 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)

    print(f"[SUCCESS] Generated distance matrix with {pair_count} routable pairs in {OUTPUT_PATH}")
    return matrix

if __name__ == "__main__":
    generate_distance_matrix()
