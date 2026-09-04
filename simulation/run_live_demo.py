import requests
import time
import json
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# The endpoint your backend teammate (Role 1) set up
API_ENDPOINT = "http://localhost:8000/api/v1/transactions/"

def trigger_presentation_demo():
    print("🎬 INITIATING PROJECT DRISHTI LIVE DEMO...")
    time.sleep(1)
    
    # The exact payload to trigger the WHERE & WHEN ML Engines
    payload = {
        "tx_id": "SIM-DEMO-2026",
        "sender_id": "ACC-VICTIM-01",
        "receiver_id": "ACC-MULE-MASTER",
        "amount": 125000.00,        # Must be > ₹50,000
        "account_type": "Mule",     # Must be "Mule"
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_known_lat": 28.6139,
        "last_known_lon": 77.2090
    }
    
    print(f"🚨 Injecting Critical Fraud Event: ₹{payload['amount']} to {payload['receiver_id']}")
    
    try:
        start_time = time.time()
        response = requests.post(API_ENDPOINT, json=payload)
        latency = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Alert successfully broadcasted to FastAPI backend (Latency: {latency:.3f}s)")
            print("👉 Check the Mapbox Radar Frontend! Top-5 ATMs should be glowing.")
        else:
            print(f"⚠️ Backend rejected the payload. Status: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ CRITICAL: FastAPI backend is not running. Start Role 1's server first.")

if __name__ == "__main__":
    trigger_presentation_demo()