import random
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Float, Integer, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class LocationType(str, enum.Enum):
    ATM = "ATM"
    BRANCH = "Branch"
    BC = "Banking_Correspondent"

class PhysicalLocation(Base):
    __tablename__ = 'physical_locations'
    location_id = Column(String, primary_key=True)
    bank_name = Column(String)
    location_type = Column(Enum(LocationType))
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    historical_fraud_count = Column(Integer)
    is_active = Column(Boolean)

def calculate_top_atms(mule_account_id: str, db: Session):
    # Fetch all active ATMs from the database
    atms = db.query(PhysicalLocation).filter(PhysicalLocation.is_active == True).all()
    
    scored_atms = []
    
    for atm in atms:
        # Generate mock distance (1.0 to 15.0 km)
        distance_km = random.uniform(1.0, 15.0)
        
        # Heuristic formula
        # Prevent division by zero just in case
        inv_distance = 1 / distance_km if distance_km > 0 else 0
        fraud_count = atm.historical_fraud_count or 0
        
        score = (fraud_count * 0.7) + (inv_distance * 0.3)
        
        scored_atms.append({
            "atm": atm,
            "distance_km": distance_km,
            "score": score
        })
        
    # Sort descending by score
    scored_atms.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top 5
    top_5 = scored_atms[:5]
    
    # Format exactly as the JSON structure expected by WebSocket client
    top_atms_payload = []
    for item in top_5:
        atm = item["atm"]
        top_atms_payload.append({
            "atm_id": atm.location_id,
            "lat": atm.latitude,
            "lng": atm.longitude,
            "score": round(item["score"], 4),
            "distance_km": round(item["distance_km"], 2),
            "fraud_count": atm.historical_fraud_count,
            "address": atm.address
        })
        
    payload = {
        "case_id": f"CASE-{mule_account_id}-AUTO",
        "top_atms": top_atms_payload,
        "time_window": "20-min"
    }
    
    return payload
