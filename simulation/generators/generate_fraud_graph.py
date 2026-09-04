"""
Simulation Data Generator: 10,000+ Historical Fraud Graph & Transactions
Project Drishti — Role 5: Data Engineer

Generates synthetic transaction history showing:
- Legitimate bank account flows
- Multi-tier mule network cascades (Victim -> Mule 1 -> Mule 2 -> Cashout)
- ATM cash withdrawals with realistic time-to-event durations (for Survival Analysis)
- Right-censored incidents (no cashout / intercepted before ATM)
- Real ATM location mappings from atms_master.csv (for Learning-to-Rank)
Saves output to simulation/data/historical_transactions.csv.
"""

import os
import csv
import random
from datetime import datetime, timedelta, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ATMS_PATH = os.path.join(DATA_DIR, "atms_master.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "historical_transactions.csv")

def generate_fraud_transactions(total_count: int = 10000):
    if not os.path.exists(ATMS_PATH):
        raise FileNotFoundError(f"{ATMS_PATH} not found. Run generate_atms.py first.")

    with open(ATMS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        atms = list(reader)

    atm_ids = [a["location_id"] for a in atms if a.get("is_active", "True") == "True"]
    hotspot_atms = [a["location_id"] for a in atms if int(a.get("historical_fraud_count", 0)) >= 5]
    if not hotspot_atms:
        hotspot_atms = atm_ids[:15]

    random.seed(1337)  # Reproducible dataset

    # Base pool of accounts
    victims = [f"ACC_VIC_{i:04d}" for i in range(1, 1500)]
    mules = [f"ACC_MULE_{i:04d}" for i in range(1, 600)]
    normals = [f"ACC_NORM_{i:04d}" for i in range(1, 3000)]

    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=60)

    print(f"[INFO] Generating {total_count} transactions across network...")

    for i in range(1, total_count + 1):
        tx_id = f"TXN-{i:07d}"
        
        # Incremental timestamp over 60 days
        tx_offset_mins = (i / total_count) * (60 * 24 * 60)
        transfer_dt = base_time + timedelta(minutes=tx_offset_mins)
        transfer_str = transfer_dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Determine transaction type:
        # 65% Normal legitimate transfers
        # 35% Fraud / Mule network transfers
        is_fraud = (random.random() < 0.35)

        if not is_fraud:
            sender = random.choice(normals)
            receiver = random.choice(normals)
            amount = round(random.uniform(500, 25000), 2)
            withdrawal_str = ""
            withdrawal_atm = ""
        else:
            # Fraud cascade: Victim -> Mule, or Mule -> Mule
            if random.random() < 0.70:
                sender = random.choice(victims)
                receiver = random.choice(mules)
            else:
                sender = random.choice(mules)
                receiver = random.choice(mules)

            amount = round(random.uniform(50000, 250000), 2)

            # Cashout event:
            # 82% successfully withdrew at ATM (Observed event)
            # 18% right-censored (police frozen account, runner fled, censored)
            is_withdrawn = (random.random() < 0.82)

            if is_withdrawn:
                # Realistic withdrawal duration: log-normal around 28-38 minutes
                duration_mins = max(8.0, random.lognormvariate(mu=3.35, sigma=0.42))
                duration_mins = min(duration_mins, 180.0)

                withdraw_dt = transfer_dt + timedelta(minutes=duration_mins)
                withdrawal_str = withdraw_dt.strftime("%Y-%m-%dT%H:%M:%S")

                # 65% chance of picking a known fraud hotspot ATM (realistic clustering!)
                if random.random() < 0.65:
                    withdrawal_atm = random.choice(hotspot_atms)
                else:
                    withdrawal_atm = random.choice(atm_ids)
            else:
                withdrawal_str = ""
                withdrawal_atm = ""

        records.append({
            "tx_id": tx_id,
            "sender_id": sender,
            "receiver_id": receiver,
            "amount": amount,
            "transfer_timestamp": transfer_str,
            "withdrawal_timestamp": withdrawal_str,
            "withdrawal_atm_id": withdrawal_atm
        })

    fieldnames = [
        "tx_id", "sender_id", "receiver_id", "amount",
        "transfer_timestamp", "withdrawal_timestamp", "withdrawal_atm_id"
    ]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    observed = sum(1 for r in records if r["withdrawal_timestamp"] != "")
    censored = sum(1 for r in records if r["receiver_id"].startswith("ACC_MULE_") and r["withdrawal_timestamp"] == "")

    print(f"[SUCCESS] Generated {len(records)} transactions in {OUTPUT_PATH}")
    print(f"[STATS] Confirmed Cashout Events: {observed} | Censored Mule Incidents: {censored}")
    return records

if __name__ == "__main__":
    generate_fraud_transactions(10000)
