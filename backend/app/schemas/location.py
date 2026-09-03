"""
FILE: backend/app/schemas/location.py
"""
from pydantic import BaseModel

class LocationResponse(BaseModel):
    atm_id: str
    latitude: float
    longitude: float
    address: str
