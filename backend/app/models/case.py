"""
FILE: backend/app/models/case.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the `Case` SQLAlchemy ORM model which represents an
    active cybercrime investigation case. When the trigger condition fires
    (mule account receives > ₹50,000), the system automatically creates a
    Case record. This Case tracks the entire lifecycle of that fraud event:
    from detection, through prediction, to outcome (confirmed interception
    or false alarm — via the human-in-the-loop feedback from Role 4's UI).

📌 WHY IS THIS FILE NEEDED?
    The Case model is the "investigation file" of Project Drishti.
    It connects the victim (who was defrauded), the mule (who received
    the funds), the prediction (which ATMs were flagged), and the final
    outcome (was the criminal caught?). This feedback loop is crucial —
    over time, confirmed/rejected cases can be used to retrain the ML model.

📌 WHAT TO IMPLEMENT HERE:

    class Case(Base):
        __tablename__ = 'cases'

        - case_id: String, primary_key=True, index=True
          A human-readable unique ID. Format: "CYB-2026-DL-00123"
          DL = Delhi, 00123 = sequential number. This format makes it easy
          for police officers to reference in official communications.

        - victim_account_id: String, ForeignKey('accounts.account_id'), nullable=False
          The account from which money was fraudulently transferred.

        - flagged_mule_id: String, ForeignKey('accounts.account_id'), nullable=True
          The mule account that received the trigger transaction.
          This is the "hot" account — the one whose cashout we are predicting.

        - compromised_amount: Float, nullable=False
          The total amount of money stolen in this fraud event (in ₹).

        - status: String, default="ACTIVE"
          The current status of this case. Possible values:
          - "ACTIVE"      → Case created, ML prediction running/completed
          - "INTERCEPTED" → Police confirmed they caught the criminal (Role 4's
                            "Confirmed Interception" button pressed)
          - "MISSED"      → Criminal withdrew and escaped before police arrived
          - "FALSE_ALARM" → Investigation revealed it was a legitimate transfer
          This field is updated by api/endpoints/cases.py PATCH endpoint.

        - created_at: DateTime, default=datetime.utcnow
          When this case was created (= when the trigger fired).
          Used to compute urgency — cases older than prediction window should
          be auto-archived.

        - prediction_payload: Text / JSON, nullable=True
          Store the full prediction JSON from the ML engine here as a string.
          This creates an audit trail: what did the AI predict for this case?
          Useful for retraining (comparing prediction vs actual outcome) and
          for generating the Police Dispatch PDF.
          Use sqlalchemy's JSON column type if on PostgreSQL, else Text.

        - predicted_atm_rank1_id: String, ForeignKey('physical_locations.location_id'), nullable=True
          The top-ranked ATM from the prediction. Denormalized here for fast
          queries like "how often was our Rank #1 prediction correct?"

📌 HOW IT CONNECTS TO OTHER FILES:
    - services/trigger_service.py CREATES a new Case when ML fires.
    - api/endpoints/cases.py provides PATCH endpoint to update case status
      (Intercepted/False Alarm from Role 4's frontend buttons).
    - Transaction.case_id references this table's case_id.
    - The WebSocket alert payload includes the case_id so the frontend
      can link updates to the correct case in the UI.
    - Long-term: case outcomes (INTERCEPTED vs MISSED) can be exported as
      training data for ML model improvement.

📌 LIBRARIES TO USE:
    - sqlalchemy (Column, String, Float, DateTime, ForeignKey, Text)
    - datetime (datetime)
    - app.db.base (Base)
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from app.db.base import Base
from datetime import datetime

class Case(Base):
    __tablename__ = 'cases'
    case_id = Column(String, primary_key=True, index=True)
    victim_account_id = Column(String, ForeignKey('accounts.account_id'), nullable=False)
    flagged_mule_id = Column(String, ForeignKey('accounts.account_id'), nullable=True)
    compromised_amount = Column(Float, nullable=False)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    prediction_payload = Column(Text, nullable=True)
