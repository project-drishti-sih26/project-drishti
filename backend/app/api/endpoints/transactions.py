"""
FILE: backend/app/api/endpoints/transactions.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This file defines the HTTP API endpoints for transaction management.
    It is the "front door" of the entire system for data ingestion.
    Role 5's `run_live_demo.py` script calls POST /api/v1/transactions
    to inject a fraud transaction, which then sets off the entire chain
    of events: trigger evaluation → ML prediction → WebSocket alert.

📌 WHY IS THIS FILE NEEDED?
    Without this endpoint, there is no way to feed transaction data into
    the system. This is the only point where external data enters the backend.
    Having it as a dedicated file (separate from the router) keeps the
    code modular and easy to test, debug, and extend.

📌 WHAT TO IMPLEMENT HERE:

    Create an APIRouter instance:
    router = APIRouter(prefix="/transactions", tags=["Transactions"])

    1. POST /transactions — INGEST A NEW TRANSACTION (The main demo trigger):
       @router.post("/", response_model=TransactionResponse, status_code=201)
       async def create_transaction(
           payload: TransactionCreate,
           db: Session = Depends(get_db)
       ):
           """
           Steps:
           1. Check if a Transaction with the same tx_id already exists in DB.
              If yes, raise HTTPException(409, "Transaction already exists").
              This prevents duplicate triggers during demo reruns.

           2. Create a new Transaction ORM object from the Pydantic payload.
              Set timestamp to datetime.utcnow() if payload.timestamp is None.

           3. Add to DB session and commit: db.add(tx), db.commit(), db.refresh(tx).

           4. Call trigger_service.evaluate_trigger(tx, db) to check if ML fires.
              This is an ASYNC call — use `await`.
              Capture the boolean return value as `trigger_fired`.

           5. Build and return a TransactionResponse with trigger_fired field.
           """

    2. GET /transactions — LIST RECENT TRANSACTIONS (for debugging/dashboard):
       @router.get("/", response_model=TransactionList)
       def get_transactions(
           skip: int = 0,
           limit: int = 50,
           db: Session = Depends(get_db)
       ):
           """
           Fetches the most recent `limit` transactions, ordered by timestamp desc.
           Used by the frontend sidebar to show a live transaction feed.
           Use db.query(Transaction).order_by(Transaction.timestamp.desc())
           .offset(skip).limit(limit).all()
           """

    3. GET /transactions/{tx_id} — GET A SINGLE TRANSACTION:
       @router.get("/{tx_id}", response_model=TransactionResponse)
       def get_transaction(tx_id: str, db: Session = Depends(get_db)):
           """
           Fetch a single transaction by tx_id.
           Raise HTTPException(404) if not found.
           """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Imports `TransactionCreate`, `TransactionResponse` from schemas/transaction.py.
    - Imports `get_db` from db/session.py.
    - Imports `Transaction` model from models/transaction.py.
    - Imports `evaluate_trigger` from services/trigger_service.py.
    - This router is registered in api/router.py with prefix /transactions.

📌 LIBRARIES TO USE:
    - fastapi (APIRouter, Depends, HTTPException, status)
    - sqlalchemy.orm (Session)
    - datetime (datetime)
    - app.schemas.transaction (TransactionCreate, TransactionResponse, TransactionList)
    - app.db.session (get_db)
    - app.models.transaction (Transaction)
    - app.services.trigger_service (evaluate_trigger)
"""
