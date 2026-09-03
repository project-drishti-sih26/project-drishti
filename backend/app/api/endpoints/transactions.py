from fastapi import APIRouter, Depends
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.db.session import SessionLocal
from app.services.trigger_service import evaluate_transaction

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, db=Depends(get_db)):
    # In a real scenario, save tx to DB here using `db`
    alert_triggered = await evaluate_transaction(tx, db)
    return TransactionResponse(status="success", alert_triggered=alert_triggered)
