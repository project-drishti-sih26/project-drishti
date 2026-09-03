import os
import random
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

# --- Self-Contained Database Setup ---
# (Since the actual models and session are still missing in the codebase, 
# this script defines them here so it can run successfully and create the SQLite DB).

DATABASE_URL = "sqlite:///./drishti.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LocationType(str, enum.Enum):
    ATM = "ATM"
    BRANCH = "Branch"
    BC = "Banking_Correspondent"

class PhysicalLocation(Base):
    __tablename__ = 'physical_locations'
    location_id = Column(String, primary_key=True, index=True)
    bank_name = Column(String, nullable=True)
    location_type = Column(Enum(LocationType), nullable=False, default=LocationType.ATM)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    historical_fraud_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

def seed_atms():
    db = SessionLocal()
    try:
        # Check if table is empty
        existing_count = db.query(PhysicalLocation).count()
        if existing_count > 0:
            print(f"[INFO] Database already seeded. Found {existing_count} ATMs.")
            return

        print("[INFO] Seeding PhysicalLocation table with dummy ATMs around Bengaluru...")
        
        # Base coordinates for Bengaluru (approximate center)
        base_lat = 12.9716
        base_lng = 77.5946

        dummy_atms = []
        banks = ["SBI", "HDFC", "ICICI", "Axis", "Kotak"]

        for i in range(1, 21):
            # Generate slight random offsets to scatter ATMs around the city
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            atm = PhysicalLocation(
                location_id=f"ATM_{random.choice(banks)}_{i:03d}",
                bank_name=f"{random.choice(banks)} Bank",
                location_type=LocationType.ATM,
                latitude=base_lat + lat_offset,
                longitude=base_lng + lng_offset,
                address=f"Dummy ATM Address {i}, Bengaluru, Karnataka",
                historical_fraud_count=random.randint(0, 50),
                is_active=True
            )
            dummy_atms.append(atm)

        # Bulk insert
        db.add_all(dummy_atms)
        db.commit()
        
        print(f"[SUCCESS] Successfully seeded 20 dummy ATMs!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_atms()
