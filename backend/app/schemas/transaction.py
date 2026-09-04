"""
FILE: backend/app/schemas/transaction.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines Pydantic schemas (data validation classes) for the
    Transaction API. Pydantic schemas are DIFFERENT from SQLAlchemy models:
    - SQLAlchemy models (in models/) → describe database table structure
    - Pydantic schemas (in schemas/) → describe what JSON data the API
      accepts (input) and returns (output) to HTTP clients.

📌 WHY IS THIS FILE NEEDED?
    When Role 5's `run_live_demo.py` sends a POST request with transaction
    JSON to the backend, FastAPI automatically validates the incoming JSON
    against the Pydantic input schema BEFORE it reaches the endpoint logic.
    If required fields are missing or the amount is a string instead of float,
    FastAPI returns a clear 422 error immediately. This prevents bad data
    from ever reaching the database or the ML engine.

📌 WHAT TO IMPLEMENT HERE:

    1. TransactionCreate (INPUT schema — what the client sends):
       class TransactionCreate(BaseModel):
           tx_id: str                           # Required: unique transaction ID
           sender_id: str                       # Required: sending account ID
           receiver_id: str                     # Required: receiving account ID
           amount: float                        # Required: must be > 0
           timestamp: Optional[datetime] = None # Optional: defaults to server time
           case_id: Optional[str] = None        # Optional: link to existing case
           transaction_type: Optional[str] = "TRANSFER"

           Add a Pydantic validator:
           @validator('amount')
           def amount_must_be_positive(cls, v):
               if v <= 0:
                   raise ValueError('Transaction amount must be positive')
               return v

    2. TransactionResponse (OUTPUT schema — what the API returns):
       class TransactionResponse(BaseModel):
           tx_id: str
           sender_id: str
           receiver_id: str
           amount: float
           timestamp: datetime
           case_id: Optional[str]
           transaction_type: str
           trigger_fired: bool  # Extra field: tells the client if ML was triggered

           class Config:
               from_attributes = True  # Allows creating from SQLAlchemy model objects

    3. TransactionList (for GET /transactions endpoint):
       class TransactionList(BaseModel):
           total: int
           transactions: List[TransactionResponse]

📌 HOW IT CONNECTS TO OTHER FILES:
    - api/endpoints/transactions.py uses `TransactionCreate` as the request
      body type and `TransactionResponse` as the return type annotation.
    - The `trigger_fired` field in `TransactionResponse` lets Role 5's
      `run_live_demo.py` confirm that the ML pipeline was activated.

📌 LIBRARIES TO USE:
    - pydantic (BaseModel, validator)
    - typing (Optional, List)
    - datetime (datetime)
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class TransactionCreate(BaseModel):
    tx_id: str
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: Optional[datetime] = None
    account_type: Optional[str] = None
    last_known_lat: Optional[float] = None
    last_known_lon: Optional[float] = None

class TransactionResponse(BaseModel):
    status: str
    alert_triggered: bool
