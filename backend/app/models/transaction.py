"""
FILE: backend/app/models/transaction.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the `Transaction` SQLAlchemy ORM model which represents
    a single money transfer event between two accounts. In graph theory terms,
    Accounts are NODES and Transactions are EDGES. The entire fraud network
    is a directed graph of these Transaction edges flowing from a victim,
    through one or more mule hops, towards a final physical cashout point.

📌 WHY IS THIS FILE NEEDED?
    This is the primary data ingestion point of the entire system.
    Role 5 (Data Engineer) pushes transactions via `run_live_demo.py`.
    Role 1's `POST /api/v1/transactions` endpoint saves them here.
    The trigger logic reads transaction data from this table to evaluate
    whether an ML prediction pipeline should be activated.

📌 WHAT TO IMPLEMENT HERE:

    class Transaction(Base):
        __tablename__ = 'transactions'

        - tx_id: String, primary_key=True, index=True
          A unique transaction identifier.
          Format: "TXN-2026-DL-00789" or UUID4 string.

        - sender_id: String, ForeignKey('accounts.account_id'), nullable=False, index=True
          The account sending the money. This is the upstream account —
          could be the victim's account (first hop) or another mule (subsequent hop).

        - receiver_id: String, ForeignKey('accounts.account_id'), nullable=False, index=True
          The account receiving the money. THIS IS THE KEY FIELD.
          When this is a Mule account AND amount > MULE_TRIGGER_AMOUNT,
          the ML engine gets triggered.
          Index this column since trigger_service queries by receiver_id frequently.

        - amount: Float, nullable=False
          The transaction amount in Indian Rupees (₹). No negative values.

        - timestamp: DateTime, default=datetime.utcnow, index=True
          When the transaction occurred. Index this for time-range queries
          and for the Survival Analysis model which needs event timestamps.

        - case_id: String, ForeignKey('cases.case_id'), nullable=True
          Optional link to a Case if this transaction is part of an active
          fraud investigation. The trigger service fills this in when a
          new case is created from this transaction.

        - transaction_type: String, default="TRANSFER"
          Type of transaction: "TRANSFER", "ATM_WITHDRAWAL", "UPI", "NEFT", "RTGS"
          ATM_WITHDRAWAL transactions are the target events the ML predicts.

📌 HOW IT CONNECTS TO OTHER FILES:
    - schemas/transaction.py defines the Pydantic input/output schemas for this model.
    - api/endpoints/transactions.py POST handler saves new transactions here.
    - services/trigger_service.py reads the newly saved transaction
      and checks receiver_id's account type + amount to trigger ML.
    - The ML WHEN engine (survival_time.py) uses `timestamp` to compute
      time-to-event durations for Survival Analysis training and inference.

📌 LIBRARIES TO USE:
    - sqlalchemy (Column, String, Float, DateTime, ForeignKey)
    - datetime (datetime) for the default timestamp value
    - app.db.base (Base)
"""
