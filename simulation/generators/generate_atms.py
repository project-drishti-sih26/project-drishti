"""
Simulation Data Generator: Delhi NCR ATM Universe
Project Drishti — Role 5: Data Engineer

Generates ~180 realistic physical cashout locations across Delhi NCR with:
- Real GPS coordinates clustered around genuine commercial corridors
- Uber H3 hexagonal indexes (Resolution 9)
- Realistic skewed historical fraud incident distribution (hotspots vs cold spots)
- Standardized CSV export to simulation/data/atms_master.csv
"""

import os
import csv
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "atms_master.csv")

# Try importing h3 for exact resolution 9 hex indexing
try:
    import h3
    HAS_H3 = True
except ImportError:
    HAS_H3 = False

# Major Delhi NCR Commercial Hubs & Clusters (Center Lat, Center Lng, Name)
DELHI_CLUSTERS = [
    (28.6315, 77.2167, "Connaught Place", "Central Delhi"),
    (28.6520, 77.1900, "Karol Bagh", "Central Delhi"),
    (28.6562, 77.2300, "Chandni Chowk", "North Delhi"),
    (28.6800, 77.2250, "Civil Lines", "North Delhi"),
    (28.7150, 77.1910, "Model Town", "North Delhi"),
    (28.5700, 77.2400, "Lajpat Nagar", "South Delhi"),
    (28.5680, 77.2220, "South Extension", "South Delhi"),
    (28.5400, 77.2400, "Greater Kailash", "South Delhi"),
    (28.5494, 77.2001, "Hauz Khas", "South Delhi"),
    (28.5244, 77.2066, "Saket District Centre", "South Delhi"),
    (28.5200, 77.1500, "Vasant Kunj", "South Delhi"),
    (28.5921, 77.0460, "Dwarka Sector 10", "West Delhi"),
    (28.6280, 77.0800, "Janakpuri District Centre", "West Delhi"),
    (28.6492, 77.1210, "Rajouri Garden", "West Delhi"),
    (28.6980, 77.1140, "Pitampura", "North West Delhi"),
    (28.7100, 77.1200, "Rohini Sector 7", "North West Delhi"),
    (28.6200, 77.2950, "Mayur Vihar Phase 1", "East Delhi"),
    (28.6300, 77.2770, "Laxmi Nagar", "East Delhi"),
    (28.6700, 77.2900, "Shahdara", "East Delhi"),
    (28.5700, 77.3200, "Noida Sector 18", "Noida NCR"),
    (28.4900, 77.0900, "Cyber Hub DLF", "Gurugram NCR"),
]

BANKS = [
    ("State Bank of India", "SBI"),
    ("HDFC Bank", "HDFC"),
    ("ICICI Bank", "ICICI"),
    ("Punjab National Bank", "PNB"),
    ("Axis Bank", "AXIS"),
    ("Bank of Baroda", "BOB"),
    ("Kotak Mahindra Bank", "KOTAK"),
    ("Union Bank of India", "UBI"),
]

LOCATION_TYPES = ["ATM", "ATM", "ATM", "Branch", "Banking_Correspondent"]

def get_h3_index(lat: float, lng: float, res: int = 9) -> str:
    if HAS_H3:
        try:
            return h3.latlng_to_cell(lat, lng, res)
        except Exception:
            pass
    # Deterministic pseudo-H3 format if h3 library is absent
    lat_q = int((lat - 28.0) * 1000)
    lng_q = int((lng - 77.0) * 1000)
    return f"891f194{abs(lat_q % 16):x}{abs(lng_q % 16):x}ffff"

def generate_atms(total_count: int = 180):
    os.makedirs(DATA_DIR, exist_ok=True)
    random.seed(42)  # Reproducible dataset

    atms = []
    atm_id_counter = 1

    per_cluster = total_count // len(DELHI_CLUSTERS) + 1

    for center_lat, center_lng, hub_name, zone in DELHI_CLUSTERS:
        for _ in range(per_cluster):
            if len(atms) >= total_count:
                break

            bank_full, bank_short = random.choice(BANKS)
            loc_type = random.choice(LOCATION_TYPES)
            
            # Scatter coordinates within ~1.2 km of the cluster center
            lat = center_lat + random.uniform(-0.011, 0.011)
            lng = center_lng + random.uniform(-0.012, 0.012)
            
            h3_idx = get_h3_index(lat, lng, 9)

            # Historical Fraud Count: Skewed Pareto-like distribution
            # 75% have 0-2 incidents, 18% have 3-5, 7% are major hotspots (6-10 incidents)
            rand_val = random.random()
            if rand_val < 0.75:
                fraud_count = random.choice([0, 0, 1, 1, 2])
            elif rand_val < 0.93:
                fraud_count = random.randint(3, 5)
            else:
                fraud_count = random.randint(6, 10)  # High risk crime hotspot

            # 96% active, 4% maintenance/inactive
            is_active = random.random() > 0.04

            location_id = f"ATM_{bank_short}_{atm_id_counter:03d}"
            address = f"{bank_short} {loc_type}, Near {hub_name}, {zone}, Delhi NCR"

            atms.append({
                "location_id": location_id,
                "bank_name": bank_full,
                "location_type": loc_type,
                "latitude": round(lat, 6),
                "longitude": round(lng, 6),
                "address": address,
                "h3_index": h3_idx,
                "historical_fraud_count": fraud_count,
                "is_active": is_active,
            })
            atm_id_counter += 1

    # Write to CSV
    fieldnames = [
        "location_id", "bank_name", "location_type", "latitude", "longitude",
        "address", "h3_index", "historical_fraud_count", "is_active"
    ]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(atms)

    print(f"[SUCCESS] Generated {len(atms)} ATMs in {OUTPUT_PATH}")
    hotspots = sum(1 for a in atms if a["historical_fraud_count"] >= 6)
    print(f"[INFO] High-Risk Hotspots (>=6 past frauds): {hotspots} ATMs")
    return atms

if __name__ == "__main__":
    generate_atms(180)
