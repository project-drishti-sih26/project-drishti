from fastapi import APIRouter, Depends
from typing import List
from app.schemas.location import LocationResponse
from app.auth import get_current_user
from app.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[LocationResponse])
@router.get("/", response_model=List[LocationResponse])
@router.get("/atms", response_model=List[LocationResponse])
def get_atms(db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    return [
        LocationResponse(atm_id="ATM-001", latitude=28.6139, longitude=77.2090, address="Connaught Place, New Delhi"),
        LocationResponse(atm_id="ATM-002", latitude=19.0760, longitude=72.8777, address="Mumbai"),
        LocationResponse(atm_id="ATM-003", latitude=12.9716, longitude=77.5946, address="Bengaluru")
    ]
