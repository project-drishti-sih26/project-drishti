import pandas as pd
import networkx as nx
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('en_IN')

def generate_transaction_graph(num_tx=10000, output_path="data/historical_tx.csv"):
    print(f"🕸️ Building synthetic mule network with {num_tx} transactions...")
    
    # Create a realistic network topology 
    G = nx.scale_free_graph(n=1000) 
    
    transactions = []
    start_time = datetime.now() - timedelta(days=30)
    
    for i in range(num_tx):
        sender = f"ACC-{random.randint(1000, 1999)}"
        receiver = f"ACC-{random.randint(1000, 1999)}"
        
        # 5% chance it's a high-value mule transfer (> 50k) to trigger the ML radar
        is_mule = random.random() < 0.05 
        
        transactions.append({
            "tx_id": f"TXN-{fake.unique.uuid4()[:8]}",
            "sender_id": sender,
            "receiver_id": receiver,
            "amount": round(random.uniform(55000, 200000) if is_mule else random.uniform(100, 5000), 2),
            "timestamp": start_time + timedelta(minutes=i*4),
            "is_mule_flag": is_mule
        })
        
    df = pd.DataFrame(transactions)
    df.to_csv(output_path, index=False)
    print(f"✅ Generated {num_tx} synthetic transactions at {output_path}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_transaction_graph()