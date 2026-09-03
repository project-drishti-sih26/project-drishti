# 📊 Role 5: Data Engineer (Synthetic World Builder)

## 📌 Ownership
* **Owner:** Data Engineer (Role 5)
* **Stack:** Python 3.11+, Faker, pandas, networkx, numpy, requests.

---

## 📂 Folder Structure
```
simulation/
├── data/
│   ├── atms_master.csv              # ~200 realistic ATMs with real coordinates in demo city
│   ├── distance_matrix.json         # Precomputed distance & travel times between H3 zones & ATMs
│   └── historical_transactions.csv  # 10,000+ past fraud transactions linking mules to ATMs
├── generators/
│   ├── generate_atms.py             # Script to generate physical ATM locations & fraud counts
│   ├── generate_distance_matrix.py  # Pre-computes travel distance matrix
│   └── generate_fraud_graph.py      # Uses Faker & networkx for synthetic mule networks
├── run_live_demo.py                 # THE DEMO TRIGGER: pushes simulated fraud into FastAPI
├── requirements.txt                 # Data generation dependencies
└── README.md                        # This guide
```

---

## 🎯 Deliverables & Key Tasks
1. **ATM Master Dataset (`data/atms_master.csv`):**
   - Generate ~200 ATMs with real GPS latitude/longitude in the demo city (e.g., New Delhi, Bengaluru, or Mumbai), bank names, and `historical_fraud_count`.
2. **Precomputed Distance Matrix (`data/distance_matrix.json`):**
   - Precompute travel times between spatial hexes and ATMs. Crucial for sub-second ML ranking during the hackathon presentation.
3. **Mule Network Graph (`data/historical_transactions.csv`):**
   - Generate 10,000 synthetic transactions using `networkx` to represent multi-hop mule account topologies.
4. **Live Presentation Trigger Script (`run_live_demo.py`):**
   - The critical script executed during judge evaluation:
     - Prompts: `Press [ENTER] to trigger Live Cyber Fraud Event...`
     - Sends `POST /api/v1/transactions` to Role 1's backend with a high-value transfer (> ₹50,000) into a known mule account.
     - Measures and prints End-to-End Latency.
