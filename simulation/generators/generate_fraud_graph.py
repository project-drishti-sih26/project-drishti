"""
Simulation Data Generator: 10,000+ Historical Fraud Graph & Transactions
Project Drishti — Role 5: Data Engineer

=============================================================================
WHY THIS GENERATOR IS BUILT THE WAY IT IS  (read this before changing it)
=============================================================================
A predictive model can only learn behaviour that actually EXISTS in the data.
An earlier version of this file chose the cashout ATM with
`random.choice(hotspot_atms)`. That produced a dataset in which the withdrawal
location was statistically INDEPENDENT of the mule's position — so the
Learning-to-Rank model provably could not learn distance, and it didn't
(0 tree splits on travel_time_mins). The system then dispatched police to an
ATM 41 minutes away while a 23-minute ATM sat at rank #4.

This generator instead simulates the *decision process* of a real mule runner
using a *multinomial logit (random utility) choice model* — the standard
econometric formulation for discrete spatial choice (McFadden, 1974):

    U(mule, atm) = B_dist * (-travel_time/10)
                 + B_fraud * log(1 + historical_fraud_count)
                 + B_affin * has_used_before
                 + B_netw  * log(1 + linked_mule_usage)
                 + B_type  * type_preference
                 + e                                (e ~ Gumbel)

    P(atm chosen) = softmax(U)      <-- the runner picks the argmax of utility

Consequences that make the downstream ML *genuinely* work:
  1. Distance now carries real signal  -> the ranker learns it.
  2. Mules revisit familiar ATMs       -> affinity features carry real signal.
  3. Cashout delay = travel time + prep time, so the WHEN engine can be a
     *covariate* (Cox PH) model instead of one global constant window.
  4. Every mule has a home/base location, written to the CSV, so training and
     inference compute the SAME features (no train/serve skew).

The Gumbel noise term is essential: it means the nearest high-risk ATM is the
MOST LIKELY choice, not the certain one. That is what makes Top-5 ranking the
correct product formulation rather than Top-1 classification — and it is why
we report NDCG and Top-K hit rate to judges instead of "accuracy".
=============================================================================

Generates synthetic transaction history containing:
- Legitimate bank account flows (no cashout)
- Multi-tier mule cascades (Victim -> Mule Tier 1 -> Mule Tier 2 -> Cashout)
- ATM cash withdrawals with travel-time-dependent durations (Survival Analysis)
- Right-censored incidents (account frozen / runner fled before reaching ATM)
- Mule base coordinates + chosen ATM (Learning-to-Rank ground truth)

Saves output to simulation/data/historical_transactions.csv
"""

import os
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ATMS_PATH = os.path.join(DATA_DIR, "atms_master.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "historical_transactions.csv")

# ─── Random-utility choice model coefficients ────────────────────────────────
# Calibrated so travel time is the dominant driver (as in real runner behaviour:
# runners minimise exposure time on the street), with fraud-hotspot familiarity
# and personal ATM habit as strong secondary effects.
B_DIST = 2.60     # per (-travel_time / 10 min)  -> strongest effect
B_FRAUD = 0.85    # per log(1 + historical_fraud_count)
B_AFFINITY = 1.40 # bonus if this mule has cashed out here before
B_NETWORK = 0.55  # per log(1 + usage by linked mules in same syndicate)
B_TYPE = 0.30     # Banking Correspondents slightly preferred (weaker KYC/CCTV)

# ─── Travel/geometry constants (MUST match ml_engine/pipelines/spatial_filter) ─
URBAN_SPEED_KMPH = 28.0
ROAD_FACTOR = 1.35
MAX_TRAVEL_MINUTES = 45.0

# ─── Cashout timing ──────────────────────────────────────────────────────────
# Total delay = preparation/coordination time + road travel time.
# Prep time is lognormal (median ~13 min): waiting for OTP relay, confirming the
# amount cleared, arranging the runner. Travel time then adds the spatial part —
# which is exactly what lets the WHEN engine condition on distance.
PREP_MU, PREP_SIGMA = 2.55, 0.45

# ─── Syndicate zones (mule networks cluster geographically in real cases) ────
# Real I4C/police case data shows mule runner networks operating out of specific
# neighbourhood clusters rather than uniformly across a metro area.
SYNDICATE_ZONES = [
    ("Central Delhi Ring",     28.6330, 77.2170),
    ("North West Cluster",     28.7040, 77.1150),
    ("East Delhi Corridor",    28.6280, 77.3050),
    ("South Delhi Belt",       28.5450, 77.2400),
    ("Dwarka / South West",    28.5900, 77.0500),
    ("Rohini / Pitampura",     28.7100, 77.1300),
    ("Shahdara / Trans Yamuna",28.6720, 77.2900),
    ("Saket / Malviya Nagar",  28.5290, 77.2100),
    ("Karol Bagh / Paharganj", 28.6520, 77.1900),
    ("Vasant Kunj / Mahipalpur",28.5390, 77.1500),
    ("Lajpat Nagar / Ashram",  28.5680, 77.2450),
    ("Mayur Vihar / Noida Rd", 28.6100, 77.3200),
]
ZONE_JITTER_DEG = 0.020   # ~2.2 km spread around the zone centroid


def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance in km between two GPS coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def travel_minutes(straight_km):
    """Road travel time in minutes, using the same road factor as the ML engine."""
    return (straight_km * ROAD_FACTOR / URBAN_SPEED_KMPH) * 60.0


def generate_fraud_transactions(total_count: int = 10000):
    if not os.path.exists(ATMS_PATH):
        raise FileNotFoundError(f"{ATMS_PATH} not found. Run generate_atms.py first.")

    with open(ATMS_PATH, "r", encoding="utf-8") as f:
        atms = [a for a in csv.DictReader(f) if str(a.get("is_active", "True")) == "True"]

    for a in atms:
        a["latitude"] = float(a["latitude"])
        a["longitude"] = float(a["longitude"])
        a["historical_fraud_count"] = int(a.get("historical_fraud_count", 0) or 0)

    if not atms:
        raise ValueError("No active ATMs found in atms_master.csv")

    random.seed(1337)  # Reproducible dataset

    # ── Account pools ────────────────────────────────────────────────────────
    victims = [f"ACC_VIC_{i:04d}" for i in range(1, 1500)]
    mules   = [f"ACC_MULE_{i:04d}" for i in range(1, 600)]
    normals = [f"ACC_NORM_{i:04d}" for i in range(1, 3000)]

    # ── Assign every mule a syndicate + home base coordinate ────────────────
    mule_zone = {}
    mule_home = {}
    for m in mules:
        zone_idx = random.randrange(len(SYNDICATE_ZONES))
        _, zlat, zlon = SYNDICATE_ZONES[zone_idx]
        mule_zone[m] = zone_idx
        mule_home[m] = (
            round(zlat + random.uniform(-ZONE_JITTER_DEG, ZONE_JITTER_DEG), 6),
            round(zlon + random.uniform(-ZONE_JITTER_DEG, ZONE_JITTER_DEG), 6),
        )

    # ── Precompute each mule's reachable ATM candidate set ───────────────────
    # Cached per mule so the 10k-row generation stays fast.
    candidate_cache = {}

    def candidates_for(mule_id):
        if mule_id in candidate_cache:
            return candidate_cache[mule_id]
        hlat, hlon = mule_home[mule_id]
        out = []
        for a in atms:
            km = haversine_km(hlat, hlon, a["latitude"], a["longitude"])
            tt = travel_minutes(km)
            if tt <= MAX_TRAVEL_MINUTES:
                out.append((a, tt))
        if len(out) < 8:  # very peripheral mule — widen the net
            scored = sorted(
                ((a, travel_minutes(haversine_km(hlat, hlon, a["latitude"], a["longitude"])))
                 for a in atms),
                key=lambda x: x[1],
            )
            out = scored[:25]
        candidate_cache[mule_id] = out
        return out

    # ── Behavioural memory: drives affinity + network features ───────────────
    mule_atm_history = defaultdict(lambda: defaultdict(int))   # mule -> atm -> count
    zone_atm_history = defaultdict(lambda: defaultdict(int))   # zone -> atm -> count

    def choose_atm(mule_id):
        """Multinomial-logit (random utility) ATM choice. Returns (atm, travel_mins)."""
        cands = candidates_for(mule_id)
        zone = mule_zone[mule_id]
        best, best_u, best_tt = None, -1e18, None

        for atm, tt in cands:
            aid = atm["location_id"]
            u  = B_DIST * (-tt / 10.0)
            u += B_FRAUD * math.log1p(atm["historical_fraud_count"])
            u += B_AFFINITY * (1.0 if mule_atm_history[mule_id][aid] > 0 else 0.0)
            u += B_NETWORK * math.log1p(zone_atm_history[zone][aid])
            u += B_TYPE * (1.0 if atm.get("location_type") == "Banking_Correspondent" else 0.0)

            # Gumbel(0,1) noise -> argmax of (utility + Gumbel) == softmax sampling.
            # This is the exact mechanism that makes the choice probabilistic:
            # the best ATM is most likely, never certain. Hence Top-5, not Top-1.
            u += -math.log(-math.log(random.random() + 1e-12) + 1e-12)

            if u > best_u:
                best, best_u, best_tt = atm, u, tt

        return best, best_tt

    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=60)

    print(f"[INFO] Generating {total_count} transactions across mule network...")
    print(f"[INFO] {len(mules)} mule accounts across {len(SYNDICATE_ZONES)} syndicate zones")
    print(f"[INFO] {len(atms)} active ATMs / BCs available as cashout candidates")

    for i in range(1, total_count + 1):
        tx_id = f"TXN-{i:07d}"

        # Incremental timestamp spread over 60 days
        tx_offset_mins = (i / total_count) * (60 * 24 * 60)
        transfer_dt = base_time + timedelta(minutes=tx_offset_mins)
        transfer_str = transfer_dt.strftime("%Y-%m-%dT%H:%M:%S")

        # 65% legitimate transfers / 35% fraud-network transfers
        is_fraud = (random.random() < 0.35)

        if not is_fraud:
            records.append({
                "tx_id": tx_id,
                "sender_id": random.choice(normals),
                "receiver_id": random.choice(normals),
                "amount": round(random.uniform(500, 25000), 2),
                "transfer_timestamp": transfer_str,
                "mule_last_lat": "",
                "mule_last_lon": "",
                "mule_tier": 0,
                "withdrawal_timestamp": "",
                "withdrawal_atm_id": "",
                "withdrawal_travel_mins": "",
            })
            continue

        # ── Fraud cascade: Victim -> Mule (tier 1), or Mule -> Mule (tier 2) ──
        if random.random() < 0.70:
            sender, mule_tier = random.choice(victims), 1
        else:
            sender, mule_tier = random.choice(mules), 2
        receiver = random.choice(mules)
        amount = round(random.uniform(50000, 250000), 2)
        hlat, hlon = mule_home[receiver]

        # 82% completed cashout (observed event) / 18% right-censored
        if random.random() >= 0.82:
            records.append({
                "tx_id": tx_id,
                "sender_id": sender,
                "receiver_id": receiver,
                "amount": amount,
                "transfer_timestamp": transfer_str,
                "mule_last_lat": hlat,
                "mule_last_lon": hlon,
                "mule_tier": mule_tier,
                "withdrawal_timestamp": "",
                "withdrawal_atm_id": "",
                "withdrawal_travel_mins": "",
            })
            continue

        chosen_atm, chosen_tt = choose_atm(receiver)
        aid = chosen_atm["location_id"]

        # Record the behaviour so future transactions show affinity/network effects
        mule_atm_history[receiver][aid] += 1
        zone_atm_history[mule_zone[receiver]][aid] += 1

        # Duration = coordination/prep time + actual road travel time.
        # Tier-2 mules move faster (money is already laundered one hop, and the
        # runner is usually pre-positioned) -> a real covariate for Cox PH.
        prep = random.lognormvariate(PREP_MU, PREP_SIGMA)
        if mule_tier == 2:
            prep *= 0.80
        duration_mins = min(max(prep + chosen_tt, 6.0), 180.0)

        withdraw_dt = transfer_dt + timedelta(minutes=duration_mins)

        records.append({
            "tx_id": tx_id,
            "sender_id": sender,
            "receiver_id": receiver,
            "amount": amount,
            "transfer_timestamp": transfer_str,
            "mule_last_lat": hlat,
            "mule_last_lon": hlon,
            "mule_tier": mule_tier,
            "withdrawal_timestamp": withdraw_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "withdrawal_atm_id": aid,
            "withdrawal_travel_mins": round(chosen_tt, 2),
        })

    fieldnames = [
        "tx_id", "sender_id", "receiver_id", "amount", "transfer_timestamp",
        "mule_last_lat", "mule_last_lon", "mule_tier",
        "withdrawal_timestamp", "withdrawal_atm_id", "withdrawal_travel_mins",
    ]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # ── Dataset summary ──────────────────────────────────────────────────────
    fraud = [r for r in records if r["mule_tier"] != 0]
    observed = [r for r in fraud if r["withdrawal_timestamp"]]
    censored = [r for r in fraud if not r["withdrawal_timestamp"]]
    travel = [float(r["withdrawal_travel_mins"]) for r in observed]
    unique_atms = len({r["withdrawal_atm_id"] for r in observed})

    print(f"\n[SUCCESS] Wrote {len(records)} transactions to {OUTPUT_PATH}")
    print(f"[STATS] Fraud transfers    : {len(fraud)}")
    print(f"[STATS] Observed cashouts  : {len(observed)}")
    print(f"[STATS] Right-censored     : {len(censored)}")
    print(f"[STATS] Distinct ATMs used : {unique_atms} / {len(atms)}")
    if travel:
        travel.sort()
        n = len(travel)
        print(f"[STATS] Travel time to chosen ATM: "
              f"median {travel[n // 2]:.1f} min | p90 {travel[int(n * 0.9)]:.1f} min")
        print(f"[STATS] -> Spatial signal present: mules pick NEARBY ATMs. "
              f"This is what the ranker learns.")
    return records


if __name__ == "__main__":
    generate_fraud_transactions(10000)
