import os
import sys
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout

test_input = {
    "mule_account_id": "MULE-X99",
    "last_latitude": 28.6315,
    "last_longitude": 77.2167,
    "transaction_amount": 150000.0,
    "transaction_timestamp": "2026-09-04T00:35:00",
    "case_id": "LIVE-VERIFY-001",
    "victim_account_id": "VICTIM-001"
}

print("=== 1. SENDING INPUT DATA TO ML ENGINE ===")
print(json.dumps(test_input, indent=2))

output = predict_fraud_cashout(test_input)

print("\n=== 2. ML ENGINE PREDICTION GENERATED ===")
print("Alert ID      :", output["alert_id"])
print("Model Used    :", output["model_used"])
print("Time Window   :", output["time_window"]["start"], "to", output["time_window"]["end"])
print("Police Window :", output["time_window"]["minutes_from_now"], "minutes")

print("\n=== 3. TOP 3 RANKED ATMs (WHERE PREDICTION) ===")
for atm in output["top_5_atms"][:3]:
    print(f"Rank #{atm['rank']}: {atm['bank_name']} | {atm['address']}")
    print(f"         Distance: {atm['distance_km']} km | ETA: {atm['travel_time_mins']} min | Score: {atm['confidence_score']}")
    print(f"         Reason: {atm['explanation']}")
