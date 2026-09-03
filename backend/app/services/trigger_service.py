"""
FILE: backend/app/services/trigger_service.py
ROLE: Role 1 — Backend Engineer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS THIS FILE?
    This is the BRAIN of the Backend — the trigger service. It contains the
    business logic that runs after every new transaction is saved to the DB.
    It checks whether the conditions for an ML fraud prediction are met,
    and if so, orchestrates the entire prediction pipeline:
    calls the ML engine → creates a Case → broadcasts the alert via WebSocket.

    Think of this as the "911 dispatcher": it receives every transaction,
    evaluates if it's an emergency, and if yes, immediately calls in all
    the resources (ML, Case creation, Alert broadcast).

📌 WHY IS THIS FILE NEEDED?
    We deliberately separate this logic from the API endpoint handler.
    The POST /transactions endpoint should ONLY validate input and save to DB.
    The trigger logic is a separate concern (business logic), and separating it:
    - Makes the code easier to test individually
    - Lets us reuse the trigger logic from other places (e.g., batch processing)
    - Keeps the endpoint handler thin and readable

📌 WHAT TO IMPLEMENT HERE:

    1. MAIN TRIGGER FUNCTION:
       async def evaluate_trigger(transaction: Transaction, db: Session) -> bool:
           """
           Evaluates whether a newly created transaction should activate
           the ML prediction pipeline.

           Logic:
           Step 1: Fetch the receiver's Account from the DB.
           Step 2: Check if receiver.account_type == AccountType.MULE
           Step 3: Check if transaction.amount >= settings.MULE_TRIGGER_AMOUNT (₹50,000)
           Step 4: If BOTH conditions are true:
               - Call `run_prediction_pipeline(transaction, receiver_account, db)`
           Step 5: Return True if triggered, False otherwise.
           """

    2. PREDICTION PIPELINE ORCHESTRATOR:
       async def run_prediction_pipeline(
           transaction: Transaction,
           mule_account: Account,
           db: Session
       ):
           """
           Orchestrates the full prediction when the trigger fires:

           Step 1: Create a new Case record in the DB.
               - Generate case_id: f"CYB-{datetime.now().strftime('%Y-%m%d')}-{uuid4().hex[:6].upper()}"
               - Set victim_account_id, flagged_mule_id, compromised_amount
               - Save to DB with status="ACTIVE"

           Step 2: Call the ML engine's inference pipeline.
               This is an import from ml_engine:
               from ml_engine.pipelines.inference_pipeline import predict_fraud_cashout

               prediction_data = predict_fraud_cashout({
                   "mule_account_id": mule_account.account_id,
                   "last_latitude": mule_account.last_known_latitude,
                   "last_longitude": mule_account.last_known_longitude,
                   "transaction_amount": transaction.amount,
                   "transaction_timestamp": transaction.timestamp.isoformat(),
                   "case_id": new_case.case_id,
                   "victim_account_id": transaction.sender_id,
               })

               NOTE: For hackathon speed, if the ML engine import doesn't exist yet,
               use a MOCK prediction function that returns hardcoded dummy data.
               This lets backend development proceed independently of ML readiness.

           Step 3: Save the prediction payload into the Case record.
               Update case.prediction_payload = json.dumps(prediction_data)
               Update case.predicted_atm_rank1_id = prediction_data["top_5_atms"][0]["location_id"]
               Commit to DB.

           Step 4: Broadcast the prediction alert via WebSocket.
               from app.services.alert_service import broadcast_alert
               await broadcast_alert(prediction_data)
           """

    3. MOCK PREDICTION FUNCTION (for testing without ML engine):
       def get_mock_prediction(transaction: Transaction, case_id: str) -> dict:
           """
           Returns a hardcoded prediction payload for local testing.
           Use this when the ML engine is not yet ready.
           Returns the same structure as the real `predict_fraud_cashout()`.
           Remove this once ml_engine is connected.
           """

📌 HOW IT CONNECTS TO OTHER FILES:
    - Called by api/endpoints/transactions.py AFTER saving a new transaction.
    - Imports ml_engine.pipelines.inference_pipeline.predict_fraud_cashout (Role 2).
    - Calls alert_service.broadcast_alert() to push the prediction to WebSocket clients.
    - Reads from models/account.py (Account) and writes to models/case.py (Case).
    - Uses settings.MULE_TRIGGER_AMOUNT from core/config.py.

📌 LIBRARIES TO USE:
    - sqlalchemy.orm (Session)
    - uuid (uuid4) for case ID generation
    - datetime (datetime)
    - json (for serializing prediction_payload)
    - asyncio (since the prediction and broadcast are async)
    - app.core.config (settings)
    - app.models.account (Account, AccountType)
    - app.models.case (Case)
    - app.models.transaction (Transaction)
"""
