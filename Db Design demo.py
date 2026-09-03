from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum
from datetime import datetime

Base = declarative_base()

# Enums for strict data validation
class AccountType(enum.Enum):
    STANDARD = "Standard"
    MULE = "Mule"

class LocationType(enum.Enum):
    ATM = "ATM"
    BRANCH = "Branch"
    BC = "Banking_Correspondent"

# 1. Accounts Table
class Account(Base):
    __tablename__ = 'accounts'
    
    account_id = Column(String, primary_key=True, index=True)
    account_type = Column(Enum(AccountType), default=AccountType.STANDARD)
    risk_score = Column(Float, default=0.0) # ML updates this

# 2. Transactions Table (The Graph Edges)
class Transaction(Base):
    __tablename__ = 'transactions'
    
    tx_id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey('accounts.account_id'))
    receiver_id = Column(String, ForeignKey('accounts.account_id'))
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Track if this specific transaction was flagged in a case
    case_id = Column(String, ForeignKey('cases.case_id'), nullable=True)

# 3. Physical Locations Table (The ATMs & Banks)
class PhysicalLocation(Base):
    __tablename__ = 'physical_locations'
    
    location_id = Column(String, primary_key=True, index=True)
    location_type = Column(Enum(LocationType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    historical_fraud_count = Column(Integer, default=0) # Crucial for the fallback heuristic

# 4. Cybercrime Cases Table
class Case(Base):
    __tablename__ = 'cases'
    
    case_id = Column(String, primary_key=True, index=True) # e.g., CYB-2026-00123
    victim_account_id = Column(String, ForeignKey('accounts.account_id'))
    compromised_amount = Column(Float, nullable=False)
    status = Column(String, default="ACTIVE")