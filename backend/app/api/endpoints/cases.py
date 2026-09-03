from fastapi import APIRouter, Depends
from typing import List
from app.schemas.case import CaseResponse
from app.auth import get_current_user
from app.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/active", response_model=List[CaseResponse])
def get_active_cases(db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    return [
        CaseResponse(case_id="CASE-001", status="ACTIVE", description="Suspicious Mule Transfer"),
        CaseResponse(case_id="CASE-002", status="ACTIVE", description="High Volume ATM Withdrawals")
    ]
