"""
FILE: backend/app/models/account.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the `Account` SQLAlchemy ORM model which maps directly
    to the `accounts` table in PostgreSQL. An Account represents either a
    legitimate bank account (Standard) or a mule account (Mule) in the
    fraud network graph. Every node in the fraud transaction graph is an Account.

📌 WHY IS THIS FILE NEEDED?
    In our system, every transaction has a sender and receiver — both are
    Accounts. The most critical field here is `account_type`. When a
    transaction arrives and the receiver's `account_type == "Mule"` AND
    `amount > ₹50,000`, the ML trigger fires. The `risk_score` field is
    updated dynamically by the ML model as it learns more about the account.

📌 WHAT TO IMPLEMENT HERE:

    1. DEFINE AN ENUM FOR ACCOUNT TYPES:
       Use Python's `enum.Enum` and SQLAlchemy's `Enum` column type.
       class AccountType(str, enum.Enum):
           STANDARD = "Standard"   # Normal victim or regular user account
           MULE = "Mule"           # A flagged mule account used for fraud routing

       Making it inherit from `str` as well allows Pydantic schemas to
       serialize/deserialize it cleanly as a plain string in JSON responses.

    2. DEFINE THE Account MODEL CLASS:
       class Account(Base):
           __tablename__ = 'accounts'

           - account_id: String, primary_key=True, index=True
             Format: "ACC_SBI_9012341234" or any unique string ID.
             Index it because we query by account_id very frequently.

           - account_type: Enum(AccountType), nullable=False, default=AccountType.STANDARD
             This is the CRITICAL field for the trigger logic.

           - risk_score: Float, default=0.0
             ML engine updates this. Range: 0.0 (clean) to 1.0 (high risk).
             The ML model recalculates this every time a suspicious transaction
             involves this account.

           - owner_name: String, nullable=True
             The name of the account holder. From simulated data.

           - bank_name: String, nullable=True
             e.g., "State Bank of India", "HDFC Bank", etc.

           - last_known_latitude: Float, nullable=True
           - last_known_longitude: Float, nullable=True
             These fields store the last known physical location of the mule runner.
             Updated when a withdrawal event is confirmed. Used by the ML spatial
             filter as the starting point for H3 candidate ATM retrieval.

📌 HOW IT CONNECTS TO OTHER FILES:
    - Imported by `app/models/__init__.py` for clean exports.
    - `Transaction.sender_id` and `Transaction.receiver_id` are ForeignKeys
      to this table's `account_id`.
    - `Case.victim_account_id` and `Case.flagged_mule_id` reference this.
    - `trigger_service.py` queries this table to check account type and
      compare the receiver account against the MULE type.
    - The ML engine reads `last_known_latitude/longitude` to start the
      spatial H3 candidate retrieval for the WHERE prediction.

📌 LIBRARIES TO USE:
    - sqlalchemy (Column, String, Float, Enum)
    - app.db.base (Base)
    - enum (standard library)
"""

from sqlalchemy import Column, String, Float, Enum as SQLAlchemyEnum
from app.db.base import Base
import enum

class AccountType(str, enum.Enum):
    STANDARD = "Standard"
    MULE = "Mule"

class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(String, primary_key=True, index=True)
    bank_name = Column(String, nullable=True)
    account_type = Column(SQLAlchemyEnum(AccountType), nullable=False, default=AccountType.STANDARD)
    risk_score = Column(Float, default=0.0)
    owner_name = Column(String, nullable=True)
    last_known_latitude = Column(Float, nullable=True)
    last_known_longitude = Column(Float, nullable=True)
