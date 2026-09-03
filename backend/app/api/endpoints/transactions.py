from fastapi import APIRouter, Depends
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.db.session import SessionLocal
from app.services.trigger_service import evaluate_transaction
from app.models.transaction import Transaction
from app.models.account import Account, AccountType

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, db=Depends(get_db)):
    # 1. Ensure foreign key accounts exist
    for acc_id, is_recv in [(tx.sender_id, False), (tx.receiver_id, True)]:
        acc = db.query(Account).filter(Account.account_id == acc_id).first()
        if not acc:
            is_mule = is_recv and (
                acc_id.startswith("MULE") or
                acc_id.startswith("ACC_MULE") or
                (tx.amount and tx.amount >= 50000.0)
            )
            db.add(Account(
                account_id=acc_id,
                account_type=AccountType.MULE if is_mule else AccountType.STANDARD,
                bank_name="Detected Bank",
                owner_name="Suspect Runner" if is_mule else "Account Holder"
            ))
            db.commit()

    # 2. Save transaction to DB
    existing_tx = db.query(Transaction).filter(Transaction.tx_id == tx.tx_id).first()
    if not existing_tx:
        data = tx.model_dump() if hasattr(tx, "model_dump") else tx.dict()
        new_tx = Transaction(**data)
        db.add(new_tx)
        db.commit()

    # 3. Trigger ML
    alert_triggered = await evaluate_transaction(tx, db)
    return TransactionResponse(status="success", alert_triggered=alert_triggered)
