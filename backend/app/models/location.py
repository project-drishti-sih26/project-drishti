"""
FILE: backend/app/models/location.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the `PhysicalLocation` SQLAlchemy ORM model which
    represents real-world physical cashout points: ATMs, Bank Branches,
    and Banking Correspondents (BCs). The ML engine's WHERE prediction
    output ranks a subset of these locations as the Top-5 most likely
    places the mule runner will visit to withdraw the stolen cash.

📌 WHY IS THIS FILE NEEDED?
    The entire purpose of Project Drishti is to predict physical locations.
    This table is the "ATM Universe" — all ~200 possible cashout locations
    loaded from Role 5's `simulation/data/atms_master.csv` during DB seeding.
    The ML spatial filter (H3 + distance matrix) uses this table to find
    reachable candidates, and the LambdaMART ranker scores them.

📌 WHAT TO IMPLEMENT HERE:

    1. LOCATION TYPE ENUM:
       class LocationType(str, enum.Enum):
           ATM = "ATM"                          # Standard ATM machines
           BRANCH = "Branch"                    # Bank branch counter
           BC = "Banking_Correspondent"         # Micro-ATM agents in rural areas

    2. THE PhysicalLocation MODEL:
       class PhysicalLocation(Base):
           __tablename__ = 'physical_locations'

           - location_id: String, primary_key=True, index=True
             Unique identifier. Format: "ATM_SBI_CONNAUGHT_001"

           - bank_name: String, nullable=True
             e.g., "State Bank of India", "HDFC Bank", "PNB"

           - location_type: Enum(LocationType), nullable=False, default=LocationType.ATM

           - latitude: Float, nullable=False
           - longitude: Float, nullable=False
             The GPS coordinates of the ATM. These are used to compute
             road distances and to display the Mapbox marker on the frontend.

           - address: String, nullable=True
             Human-readable address for the Police Dispatch PDF.
             e.g., "Janpath Road, Connaught Place, New Delhi - 110001"

           - h3_index: String, nullable=True, index=True
             The Uber H3 hexagonal cell index (at resolution 9) that contains
             this ATM. Pre-computed and stored here to avoid re-computing during
             inference. The ML spatial filter groups ATMs by h3_index to
             rapidly find candidates within neighboring hex cells.
             Index this column since spatial_filter.py queries it frequently.

           - historical_fraud_count: Integer, default=0
             Number of confirmed fraud withdrawals ever recorded at this ATM.
             This is the MOST IMPORTANT feature for the ML ranking model.
             High fraud count = higher probability of being chosen by mules again.
             Also used in the cold-start fallback heuristic formula.

           - is_active: Boolean, default=True
             Whether this ATM is currently operational. The ML filter
             should exclude inactive ATMs from candidates.

📌 HOW IT CONNECTS TO OTHER FILES:
    - simulation/data/atms_master.csv is loaded into this table via a seeding
      script written by Role 5 (Data Engineer).
    - ml_engine/pipelines/spatial_filter.py reads this table (via API call or
      direct DB query) to fetch candidate ATMs for the WHERE engine.
    - ml_engine/models/fallback_heuristic.py uses `historical_fraud_count` field.
    - The final prediction payload sent over WebSocket contains fields from
      this table (location_id, bank_name, latitude, longitude, address).
    - Frontend (Role 3) uses latitude/longitude to place Mapbox markers.

📌 LIBRARIES TO USE:
    - sqlalchemy (Column, String, Float, Integer, Boolean, Enum)
    - app.db.base (Base)
    - enum (standard library)
"""
