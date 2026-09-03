import time
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/v1/transactions"

def send_transaction(tx_id, sender, receiver, amount):
    payload = {
        "tx_id": tx_id,
        "sender_id": sender,
        "receiver_id": receiver,
        "amount": amount,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send transaction {tx_id}: {e}")
        return None

def run_demo():
    print("="*60)
    print("🚀 DRISHTI LIVE DEMO INITIALIZED 🚀")
    print("="*60)
    print("[INFO] Simulating standard banking traffic...")
    time.sleep(1)

    # 1. Normal Transaction
    print(f"\n[INFO] {datetime.now().strftime('%H:%M:%S')} - Routing funds: ACC-101 -> ACC-902 (₹2,500.00)")
    send_transaction("TXN-001", "ACC-101", "ACC-902", 2500.0)
    time.sleep(1.5)

    # 2. Normal Transaction
    print(f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Routing funds: ACC-404 -> ACC-511 (₹8,000.00)")
    send_transaction("TXN-002", "ACC-404", "ACC-511", 8000.0)
    time.sleep(1.5)

    # 3. Normal Transaction
    print(f"[INFO] {datetime.now().strftime('%H:%M:%S')} - Routing funds: ACC-777 -> ACC-303 (₹1,200.00)")
    send_transaction("TXN-003", "ACC-777", "ACC-303", 1200.0)
    time.sleep(1.5)

    # 4. Critical Mule Transaction
    print("\n" + "!"*60)
    print(f"[ALERT] {datetime.now().strftime('%H:%M:%S')} - SUSPICIOUS ENDPOINT DETECTED")
    print("!"*60)
    print("[WARNING] High-value transfer to known flagged account pattern.")
    print("[INFO] Routing funds: VICTIM-001 -> MULE-X99 (₹1,50,000.00)")
    
    response = send_transaction("TXN-999", "VICTIM-001", "MULE-X99", 150000.0)
    
    if response and response.get('alert_triggered'):
        print("[SUCCESS] ML Engine triggered! WebSocket payload broadcasted.")
    else:
        print("[FAIL] ML Engine did not trigger or request failed.")
        
    print("\n[INFO] Demo sequence complete.")

if __name__ == "__main__":
    run_demo()
