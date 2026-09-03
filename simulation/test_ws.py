import asyncio
import websockets
import json

WS_URL = "ws://127.0.0.1:8000/ws/alerts"

async def listen():
    print("="*60)
    print("🛡️  DRISHTI ALERT MONITOR ACTIVE 🛡️")
    print(f"[INFO] Connecting to {WS_URL}...")
    print("="*60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("[SUCCESS] Connected to alert stream. Waiting for triggers...\n")
            while True:
                message = await websocket.recv()
                print("🚨 [ALERT RECEIVED] 🚨")
                try:
                    data = json.loads(message)
                    print(json.dumps(data, indent=4))
                except json.JSONDecodeError:
                    print(message)
                print("-"*60)
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(listen())
