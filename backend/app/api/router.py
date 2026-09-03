from fastapi import APIRouter
from app.api.endpoints import transactions, cases, locations, websockets

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
# Websockets don't usually have the /api/v1 prefix, but according to prompt it's in api_router. 
# We'll prefix it with /ws
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])
